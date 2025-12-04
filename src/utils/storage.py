"""Storage utilities using GitHub Gist"""

import logging
import json
import requests
from typing import Dict, Optional, Any
from src.utils.config import GIST_TOKEN

logger = logging.getLogger(__name__)

# GitHub Gist API
GIST_API_URL = "https://api.github.com/gists"


def _get_headers() -> Dict[str, str]:
    """Get headers for Gist API requests"""
    if not GIST_TOKEN:
        logger.warning("GIST_TOKEN not set, Gist operations will fail")
        return {}
    
    return {
        "Authorization": f"token {GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }


def create_gist(filename: str, content: str, description: str = "Bot state storage") -> Optional[str]:
    """
    Create a new Gist
    
    Args:
        filename: Name of the file in Gist
        content: Content to store
        description: Gist description
    
    Returns:
        Gist ID or None
    """
    if not GIST_TOKEN:
        logger.error("GIST_TOKEN not set, cannot create Gist")
        return None
    
    try:
        data = {
            "description": description,
            "public": False,
            "files": {
                filename: {
                    "content": content
                }
            }
        }
        
        response = requests.post(GIST_API_URL, json=data, headers=_get_headers(), timeout=10)
        response.raise_for_status()
        
        gist_data = response.json()
        gist_id = gist_data.get("id")
        logger.info(f"Created Gist: {gist_id}")
        return gist_id
        
    except Exception as e:
        logger.error(f"Failed to create Gist: {e}")
        return None


def update_gist(gist_id: str, filename: str, content: str) -> bool:
    """
    Update an existing Gist
    
    Args:
        gist_id: Gist ID
        filename: Name of the file in Gist
        content: New content
    
    Returns:
        True if successful
    """
    if not GIST_TOKEN:
        logger.error("GIST_TOKEN not set, cannot update Gist")
        return False
    
    try:
        # First, get the current Gist to preserve other files
        get_response = requests.get(f"{GIST_API_URL}/{gist_id}", headers=_get_headers(), timeout=10)
        get_response.raise_for_status()
        current_gist = get_response.json()
        
        # Prepare files dict
        files = {}
        for file_name, file_info in current_gist.get("files", {}).items():
            files[file_name] = {"content": file_info.get("content", "")}
        
        # Update or add the target file
        files[filename] = {"content": content}
        
        # Update Gist
        data = {
            "files": files
        }
        
        response = requests.patch(
            f"{GIST_API_URL}/{gist_id}",
            json=data,
            headers=_get_headers(),
            timeout=10
        )
        response.raise_for_status()
        
        logger.info(f"Updated Gist: {gist_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update Gist: {e}")
        return False


def get_gist(gist_id: str, filename: str) -> Optional[str]:
    """
    Get content from a Gist
    
    Args:
        gist_id: Gist ID
        filename: Name of the file in Gist
    
    Returns:
        File content or None
    """
    try:
        response = requests.get(f"{GIST_API_URL}/{gist_id}", headers=_get_headers(), timeout=10)
        response.raise_for_status()
        
        gist_data = response.json()
        files = gist_data.get("files", {})
        
        if filename in files:
            content = files[filename].get("content", "")
            logger.info(f"Retrieved content from Gist: {gist_id}")
            return content
        else:
            logger.warning(f"File {filename} not found in Gist {gist_id}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to get Gist: {e}")
        return None


def save_state(state: Dict[str, Any], gist_id: Optional[str] = None, filename: str = "bot_state.json") -> Optional[str]:
    """
    Save state to Gist
    
    Args:
        state: State dictionary to save
        gist_id: Existing Gist ID (if None, creates new)
        filename: Filename in Gist
    
    Returns:
        Gist ID or None
    """
    try:
        content = json.dumps(state, indent=2, ensure_ascii=False)
        
        if gist_id:
            success = update_gist(gist_id, filename, content)
            return gist_id if success else None
        else:
            return create_gist(filename, content, "Proactive AI Bot State")
            
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
        return None


def load_state(gist_id: str, filename: str = "bot_state.json") -> Optional[Dict[str, Any]]:
    """
    Load state from Gist
    
    Args:
        gist_id: Gist ID
        filename: Filename in Gist
    
    Returns:
        State dictionary or None
    """
    try:
        content = get_gist(gist_id, filename)
        if content:
            state = json.loads(content)
            logger.info(f"Loaded state from Gist: {gist_id}")
            return state
        return None
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse state JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load state: {e}")
        return None

