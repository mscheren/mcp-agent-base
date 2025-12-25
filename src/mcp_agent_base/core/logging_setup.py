"""Simple logging configuration for mcp-agent-base."""

import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "ENDC": "\033[0m",  # End color
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        level = record.levelname
        color = self.COLORS.get(level, "")
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format the message
        message = record.getMessage()
        formatted = f"{color}[{timestamp}] [{level}] {record.name}: {message}{self.COLORS['ENDC']}"
        return formatted


def setup_logging(
    level: int = logging.INFO,
    use_colors: bool = True,
    logger_name: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for mcp-agent-base.

    Args:
        level: Logging level (default: INFO).
        use_colors: Whether to use colored output (default: True).
        logger_name: Specific logger name, or None for root mcp_agent_base logger.

    Returns:
        Configured logger instance.
    """
    # Get the logger for mcp_agent_base package
    logger = logging.getLogger(logger_name or "mcp_agent_base")
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Set formatter
    if use_colors:
        console_handler.setFormatter(ColoredFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        )

    logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger
