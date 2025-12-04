"""Enhanced logging utilities"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

# Usage tracking
_usage_stats: Dict[str, int] = {}


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
):
    """
    Setup logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        format_string: Optional custom format string
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format=format_string,
        handlers=handlers,
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def log_execution(command: str, success: bool, duration: Optional[float] = None):
    """
    Log command execution
    
    Args:
        command: Command name
        success: Whether execution was successful
        duration: Execution duration in seconds
    """
    status = "SUCCESS" if success else "FAILED"
    duration_str = f" ({duration:.2f}s)" if duration else ""
    
    logger = logging.getLogger(__name__)
    logger.info(f"Execution: {command} - {status}{duration_str}")
    
    # Track usage
    _usage_stats[command] = _usage_stats.get(command, 0) + 1
    if success:
        _usage_stats[f"{command}_success"] = _usage_stats.get(f"{command}_success", 0) + 1
    else:
        _usage_stats[f"{command}_failed"] = _usage_stats.get(f"{command}_failed", 0) + 1


def log_api_call(service: str, endpoint: str, success: bool, duration: Optional[float] = None):
    """
    Log API call
    
    Args:
        service: Service name (e.g., "OpenWeather", "Gemini")
        endpoint: API endpoint
        success: Whether call was successful
        duration: Call duration in seconds
    """
    status = "SUCCESS" if success else "FAILED"
    duration_str = f" ({duration:.2f}s)" if duration else ""
    
    logger = logging.getLogger(__name__)
    logger.info(f"API Call: {service} - {endpoint} - {status}{duration_str}")


def get_usage_stats() -> Dict[str, int]:
    """
    Get usage statistics
    
    Returns:
        Dictionary of usage statistics
    """
    return _usage_stats.copy()


def reset_usage_stats():
    """Reset usage statistics"""
    global _usage_stats
    _usage_stats = {}


def log_error_with_context(error: Exception, context: Dict[str, str]):
    """
    Log error with additional context
    
    Args:
        error: Exception object
        context: Additional context dictionary
    """
    logger = logging.getLogger(__name__)
    context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
    logger.error(f"Error: {error} | Context: {context_str}", exc_info=True)

