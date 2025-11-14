"""
PROJECT LUMEN - Logging Utilities
Centralized logging configuration
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from backend.config import settings


def setup_logger(name: str = "lumen") -> logging.Logger:
    """
    Set up a logger with file and console handlers

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # File handler
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()


def log_operation(operation: str, details: dict):
    """
    Log an operation with structured details

    Args:
        operation: Operation name
        details: Operation details
    """
    logger.info(f"OPERATION: {operation} | DETAILS: {details}")


def log_error(error: Exception, context: str = ""):
    """
    Log an error with context

    Args:
        error: Exception object
        context: Additional context about where error occurred
    """
    logger.error(f"ERROR in {context}: {type(error).__name__}: {str(error)}", exc_info=True)


def log_agent_action(agent_name: str, action: str, result: dict):
    """
    Log agent actions for auditability

    Args:
        agent_name: Name of the agent
        action: Action performed
        result: Action result
    """
    logger.info(f"AGENT: {agent_name} | ACTION: {action} | RESULT: {result}")
