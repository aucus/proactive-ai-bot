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
# Use memento_gemini collection for projects (entityType = "Project")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "memento_gemini")

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
    Check if Qdrant collection exists
    For memento_gemini, we assume it already exists (created by Memento system)
    
    Returns:
        True if collection exists
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
        else:
            logger.warning(f"Collection '{QDRANT_COLLECTION}' not found (status: {response.status_code})")
            return False
    except Exception as e:
        logger.error(f"Failed to check collection: {e}")
        return False


def search_projects_from_qdrant(query: str = "active projects 진행중", limit: int = 5) -> List[Dict]:
    """
    Search projects from Qdrant vector database (memento_gemini collection)
    Filters by entityType = "Project" and prioritizes warm/hot tier projects
    
    Args:
        query: Search query (optional, uses filter if not provided)
        limit: Maximum number of results
    
    Returns:
        List of project dictionaries
    """
    if not QDRANT_URL or not QDRANT_API_KEY:
        logger.warning("Qdrant not configured, skipping search")
        return []
    
    try:
        # Check collection exists (memento_gemini should already exist)
        if not _ensure_collection():
            logger.warning("Collection not available, skipping search")
            return []
        
        # Use scroll API with filter to get projects by entityType
        url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/scroll"
        headers = {
            "api-key": QDRANT_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Filter for entityType = "Project"
        payload = {
            "limit": limit * 2,  # Get more to filter by memory_tier
            "with_payload": True,
            "filter": {
                "must": [
                    {
                        "key": "entityType",
                        "match": {
                            "value": "Project"
                        }
                    }
                ]
            }
        }
        
        logger.info(f"Searching Qdrant for projects (entityType=Project), limit: {limit}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        points = data.get("result", {}).get("points", [])
        
        logger.info(f"Qdrant returned {len(points)} project points")
        
        projects = []
        for point in points:
            payload_data = point.get("payload", {})
            if not payload_data:
                continue
            
            name = payload_data.get("name", "")
            if not name:
                continue
            
            # Parse observations (stored as JSON string)
            observations = payload_data.get("observations", "")
            next_actions = []
            if observations:
                try:
                    import ast
                    obs_list = ast.literal_eval(observations) if isinstance(observations, str) else observations
                    if isinstance(obs_list, list):
                        # Extract first few observations as next actions
                        next_actions = [obs[:100] for obs in obs_list[:3] if obs]
                except Exception as e:
                    logger.debug(f"Failed to parse observations: {e}")
            
            memory_tier = payload_data.get("memory_tier", "cold")
            last_accessed = payload_data.get("last_accessed", "")
            
            # Determine status based on memory_tier
            if memory_tier in ["hot", "warm"]:
                status = "active"
            elif memory_tier == "archive":
                status = "archived"
            else:
                status = "active"  # Default to active for cold tier
            
            project = {
                "title": name,
                "status": status,
                "next_actions": next_actions,
                "source": "qdrant",
                "memory_tier": memory_tier,
                "last_accessed": last_accessed,
                "score": 1.0  # All projects match the filter
            }
            projects.append(project)
        
        # Sort by memory_tier priority (hot > warm > cold > archive)
        tier_priority = {"hot": 0, "warm": 1, "cold": 2, "archive": 3}
        projects.sort(key=lambda p: tier_priority.get(p.get("memory_tier", "cold"), 3))
        
        logger.info(f"Parsed {len(projects)} projects from Qdrant (prioritized by memory_tier)")
        return projects[:limit]  # Return top N projects
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to search Qdrant: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text[:500]}")
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
                logger.info(f"Scanning project path: {project_path}")
                # Scan both files and subdirectories
                for item in os.listdir(project_path):
                    item_path = os.path.join(project_path, item)
                    if os.path.isfile(item_path) and item.endswith(".md"):
                        try:
                            with open(item_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                
                                # Extract project info from frontmatter or content
                                project = _parse_obsidian_project(item, content)
                                if project:
                                    projects.append(project)
                                    logger.debug(f"Found project: {project['title']}")
                        except Exception as e:
                            logger.warning(f"Failed to read {item_path}: {e}")
                    elif os.path.isdir(item_path):
                        # Also check subdirectories for project files
                        try:
                            for sub_item in os.listdir(item_path):
                                if sub_item.endswith(".md"):
                                    sub_item_path = os.path.join(item_path, sub_item)
                                    try:
                                        with open(sub_item_path, "r", encoding="utf-8") as f:
                                            content = f.read()
                                            project = _parse_obsidian_project(sub_item, content)
                                            if project:
                                                projects.append(project)
                                                logger.debug(f"Found project in subdirectory: {project['title']}")
                                    except Exception as e:
                                        logger.warning(f"Failed to read {sub_item_path}: {e}")
                        except Exception as e:
                            logger.warning(f"Failed to scan subdirectory {item_path}: {e}")
        
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
    logger.info("Starting project reminders retrieval...")
    logger.info(f"QDRANT_URL configured: {bool(QDRANT_URL)}")
    logger.info(f"QDRANT_API_KEY configured: {bool(QDRANT_API_KEY)}")
    logger.info(f"OBSIDIAN_VAULT_PATH configured: {bool(OBSIDIAN_VAULT_PATH)}")
    
    projects = []
    
    # Try Qdrant first
    if QDRANT_URL and QDRANT_API_KEY:
        logger.info("Attempting to search projects from Qdrant...")
        qdrant_projects = search_projects_from_qdrant()
        logger.info(f"Found {len(qdrant_projects)} projects from Qdrant")
        projects.extend(qdrant_projects)
    else:
        logger.warning("Qdrant not configured (URL or API key missing)")
    
    # Fallback to Obsidian and sync to Qdrant
    if not projects:
        logger.info("No projects from Qdrant, trying Obsidian fallback...")
        obsidian_projects = get_projects_from_obsidian()
        logger.info(f"Found {len(obsidian_projects)} projects from Obsidian")
        projects.extend(obsidian_projects)
        
        # Sync to Qdrant for future use
        if obsidian_projects and QDRANT_URL and QDRANT_API_KEY:
            logger.info("Syncing Obsidian projects to Qdrant...")
            sync_success = sync_projects_to_qdrant(obsidian_projects)
            logger.info(f"Sync to Qdrant: {'success' if sync_success else 'failed'}")
    
    # If no projects found, return placeholder
    if not projects:
        logger.warning("No projects found from any source, returning placeholder")
        logger.warning(f"Qdrant search attempted: {bool(QDRANT_URL and QDRANT_API_KEY)}")
        logger.warning(f"Obsidian fallback attempted: {bool(OBSIDIAN_VAULT_PATH)}")
        return {
            "projects": [],
            "has_projects": False,
            "message": "현재 진행 중인 프로젝트가 없어요. 새로운 프로젝트를 시작해볼까요? 🚀"
        }
    
    # Filter active projects
    active_projects = [p for p in projects if p.get("status", "").lower() in ["active", "진행중", ""]]
    logger.info(f"Filtered to {len(active_projects)} active projects (from {len(projects)} total)")
    
    return {
        "projects": active_projects[:5],  # Limit to 5 projects
        "has_projects": len(active_projects) > 0,
        "count": len(active_projects),
        "timestamp": datetime.now().isoformat()
    }


