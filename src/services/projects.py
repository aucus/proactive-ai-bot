"""Project reminder service using Obsidian/Qdrant"""

import logging
import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Qdrant configuration (optional)
QDRANT_URL = os.getenv("QDRANT_URL", "").rstrip("/")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "projects")

# Obsidian vault path (optional)
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")

# Gemini API for embeddings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def _get_embedding(text: str) -> Optional[List[float]]:
    """
    Get embedding vector from Gemini API
    
    Args:
        text: Text to embed
    
    Returns:
        Embedding vector or None
    """
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not configured, cannot generate embeddings")
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Use Gemini embedding model (gemini-embedding-001)
        # Output dimensionality: 768 (matches Qdrant collection size)
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        
        # Handle different response formats
        if result:
            if isinstance(result, dict) and "embedding" in result:
                return result["embedding"]
            elif hasattr(result, "embedding"):
                return result.embedding
            elif isinstance(result, list) and len(result) > 0:
                # New API format returns list
                if hasattr(result[0], "values"):
                    return result[0].values
                elif isinstance(result[0], dict) and "values" in result[0]:
                    return result[0]["values"]
        
        # Fallback: try gemini-embedding-001 via REST API
        try:
            import requests
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={GEMINI_API_KEY}"
            payload = {
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": text}]},
                "taskType": "RETRIEVAL_DOCUMENT"
            }
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "embedding" in data and "values" in data["embedding"]:
                return data["embedding"]["values"]
        except Exception as e2:
            logger.warning(f"Fallback embedding API also failed: {e2}")
        
        return None
    except Exception as e:
        logger.error(f"Failed to get embedding: {e}", exc_info=True)
        return None


def _ensure_collection() -> bool:
    """
    Ensure Qdrant collection exists
    
    Returns:
        True if collection exists or was created
    """
    if not QDRANT_URL or not QDRANT_API_KEY:
        return False
    
    try:
        # Check if collection exists
        url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}"
        headers = {"api-key": QDRANT_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Collection '{QDRANT_COLLECTION}' exists")
            return True
        elif response.status_code == 404:
            # Create collection
            logger.info(f"Creating collection '{QDRANT_COLLECTION}'")
            create_url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}"
            create_payload = {
                "vectors": {
                    "size": 768,  # Gemini embedding dimension (text-embedding-004 or embedding-001)
                    "distance": "Cosine"
                }
            }
            create_response = requests.put(create_url, json=create_payload, headers=headers, timeout=10)
            if create_response.status_code in [200, 201]:
                logger.info(f"Collection '{QDRANT_COLLECTION}' created successfully")
                return True
            else:
                logger.error(f"Failed to create collection: {create_response.status_code} - {create_response.text}")
                return False
        else:
            logger.error(f"Failed to check collection: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to ensure collection: {e}")
        return False


def search_projects_from_qdrant(query: str = "active projects 진행중", limit: int = 5) -> List[Dict]:
    """
    Search projects from Qdrant vector database
    
    Args:
        query: Search query
        limit: Maximum number of results
    
    Returns:
        List of project dictionaries
    """
    if not QDRANT_URL or not QDRANT_API_KEY:
        logger.warning("Qdrant not configured, skipping search")
        return []
    
    try:
        # Ensure collection exists
        if not _ensure_collection():
            logger.warning("Collection not available, skipping search")
            return []
        
        # Get query embedding
        query_embedding = _get_embedding(query)
        if not query_embedding:
            logger.warning("Failed to get query embedding, skipping search")
            return []
        
        # Search in Qdrant
        url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search"
        headers = {
            "api-key": QDRANT_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "vector": query_embedding,
            "limit": limit,
            "with_payload": True,
            "score_threshold": 0.5  # Minimum similarity score
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("result", [])
        
        projects = []
        for result in results:
            payload_data = result.get("payload", {})
            if payload_data:
                project = {
                    "title": payload_data.get("title", ""),
                    "status": payload_data.get("status", "active"),
                    "next_actions": payload_data.get("next_actions", []),
                    "source": "qdrant",
                    "score": result.get("score", 0.0)
                }
                projects.append(project)
        
        logger.info(f"Found {len(projects)} projects from Qdrant")
        return projects
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to search Qdrant: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error searching Qdrant: {e}", exc_info=True)
        return []


def get_projects_from_obsidian() -> List[Dict]:
    """
    Get active projects from Obsidian vault
    
    Returns:
        List of project dictionaries
    """
    if not OBSIDIAN_VAULT_PATH or not os.path.exists(OBSIDIAN_VAULT_PATH):
        logger.warning("Obsidian vault path not configured or not found")
        return []
    
    try:
        projects = []
        
        # Look for project files in common locations
        # Support both PARA structure and flat structure
        project_paths = [
            # PARA structure (priority)
            os.path.join(OBSIDIAN_VAULT_PATH, "2. PARA", "1. Projects"),
            os.path.join(OBSIDIAN_VAULT_PATH, "2. PARA", "1. Projects"),
            # Flat structure (fallback)
            os.path.join(OBSIDIAN_VAULT_PATH, "Projects"),
            os.path.join(OBSIDIAN_VAULT_PATH, "projects"),
            os.path.join(OBSIDIAN_VAULT_PATH, "Active Projects"),
        ]
        
        for project_path in project_paths:
            if os.path.exists(project_path):
                for filename in os.listdir(project_path):
                    if filename.endswith(".md"):
                        filepath = os.path.join(project_path, filename)
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                content = f.read()
                                
                                # Extract project info from frontmatter or content
                                project = _parse_obsidian_project(filename, content)
                                if project:
                                    projects.append(project)
                        except Exception as e:
                            logger.warning(f"Failed to read {filepath}: {e}")
        
        logger.info(f"Found {len(projects)} projects from Obsidian")
        return projects
        
    except Exception as e:
        logger.error(f"Failed to get projects from Obsidian: {e}")
        return []


def _parse_obsidian_project(filename: str, content: str) -> Optional[Dict]:
    """
    Parse project information from Obsidian markdown file
    
    Args:
        filename: Markdown filename
        content: File content
    
    Returns:
        Project dictionary or None
    """
    try:
        # Extract title from filename
        title = filename.replace(".md", "").strip()
        
        # Look for frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                # Parse YAML-like frontmatter (simplified)
                # Support both "status:" and "project_status:" fields
                status = "active"
                status_found = False
                
                for line in frontmatter.split("\n"):
                    line_lower = line.lower().strip()
                    # Check for status: or project_status:
                    if line_lower.startswith("status:") or line_lower.startswith("project_status:"):
                        status = line.split(":")[-1].strip().lower()
                        status_found = True
                        break
                
                # Only return active projects
                # Support: active, 진행중, 진행, in-progress
                if status_found:
                    active_keywords = ["active", "진행중", "진행", "in-progress", "in_progress"]
                    if not any(keyword in status for keyword in active_keywords):
                        return None
        
        # Look for TODO items or next actions
        next_actions = []
        for line in content.split("\n"):
            if "- [ ]" in line or "- [x]" in line:
                action = line.replace("- [ ]", "").replace("- [x]", "").strip()
                if action and len(action) < 100:
                    next_actions.append(action)
                    if len(next_actions) >= 3:
                        break
        
        return {
            "title": title,
            "status": "active",
            "next_actions": next_actions[:3],
            "source": "obsidian"
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse project: {e}")
        return None


def sync_projects_to_qdrant(projects: List[Dict]) -> bool:
    """
    Sync projects from Obsidian to Qdrant
    
    Args:
        projects: List of project dictionaries
    
    Returns:
        True if successful
    """
    if not QDRANT_URL or not QDRANT_API_KEY or not projects:
        return False
    
    try:
        # Ensure collection exists
        if not _ensure_collection():
            return False
        
        # Prepare points for upsert
        points = []
        for idx, project in enumerate(projects):
            # Create text for embedding
            title = project.get("title", "")
            description = " ".join(project.get("next_actions", []))
            text = f"{title} {description}".strip()
            
            if not text:
                continue
            
            # Get embedding
            embedding = _get_embedding(text)
            if not embedding:
                logger.warning(f"Failed to get embedding for project: {title}")
                continue
            
            # Create point
            point = {
                "id": hash(title) % (2**63),  # Use hash as ID
                "vector": embedding,
                "payload": {
                    "title": title,
                    "status": project.get("status", "active"),
                    "next_actions": project.get("next_actions", []),
                    "source": "obsidian",
                    "updated_at": datetime.now().isoformat()
                }
            }
            points.append(point)
        
        if not points:
            logger.warning("No valid points to sync")
            return False
        
        # Upsert points
        url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points"
        headers = {
            "api-key": QDRANT_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "points": points
        }
        
        response = requests.put(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Synced {len(points)} projects to Qdrant")
        return True
        
    except Exception as e:
        logger.error(f"Failed to sync projects to Qdrant: {e}", exc_info=True)
        return False


def get_project_reminders() -> Dict:
    """
    Get project reminders for evening
    
    Returns:
        Dictionary with project reminders
    """
    projects = []
    
    # Try Qdrant first
    if QDRANT_URL and QDRANT_API_KEY:
        qdrant_projects = search_projects_from_qdrant()
        projects.extend(qdrant_projects)
    
    # Fallback to Obsidian and sync to Qdrant
    if not projects:
        obsidian_projects = get_projects_from_obsidian()
        projects.extend(obsidian_projects)
        
        # Sync to Qdrant for future use
        if obsidian_projects and QDRANT_URL and QDRANT_API_KEY:
            logger.info("Syncing Obsidian projects to Qdrant...")
            sync_projects_to_qdrant(obsidian_projects)
    
    # If no projects found, return placeholder
    if not projects:
        logger.info("No projects found, returning placeholder reminder")
        return {
            "projects": [],
            "has_projects": False,
            "message": "현재 진행 중인 프로젝트가 없어요. 새로운 프로젝트를 시작해볼까요? 🚀"
        }
    
    # Filter active projects
    active_projects = [p for p in projects if p.get("status", "").lower() in ["active", "진행중", ""]]
    
    return {
        "projects": active_projects[:5],  # Limit to 5 projects
        "has_projects": len(active_projects) > 0,
        "count": len(active_projects),
        "timestamp": datetime.now().isoformat()
    }


