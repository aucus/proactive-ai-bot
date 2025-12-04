"""Project reminder service using Obsidian/Qdrant"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Qdrant configuration (optional)
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "projects")

# Obsidian vault path (optional)
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")


def search_projects_from_qdrant(query: str = "active projects", limit: int = 5) -> List[Dict]:
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
        import requests
        
        # Qdrant search endpoint
        url = f"{QDRANT_URL}/collections/{QDRANT_COLLECTION}/points/search"
        
        # For now, return empty list - actual implementation requires embedding
        # TODO: Implement vector search with embedding model
        logger.info("Qdrant search not fully implemented yet")
        return []
        
    except Exception as e:
        logger.error(f"Failed to search Qdrant: {e}")
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
        project_paths = [
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
                status = "active"
                if "status:" in frontmatter.lower():
                    for line in frontmatter.split("\n"):
                        if "status:" in line.lower():
                            status = line.split(":")[-1].strip().lower()
                            break
                
                # Only return active projects
                if "active" not in status and "진행중" not in status:
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
    
    # Fallback to Obsidian
    if not projects:
        obsidian_projects = get_projects_from_obsidian()
        projects.extend(obsidian_projects)
    
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

