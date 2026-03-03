"""Logging module for Vulnerability Scanner.

Provides structured logging with both file and console output.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class LoggerManager:
    """Manage application logging."""

    def __init__(self, log_dir: str = "logs"):
        """Initialize logger manager.
        
        Args:
            log_dir: Directory to store log files.
        """
        self.log_dir = log_dir
        self._ensure_log_dir()
        self.logger = self._setup_logger()

    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def _setup_logger(self) -> logging.Logger:
        """Set up logger with file and console handlers.
        
        Returns:
            Configured logger instance.
        """
        logger = logging.getLogger("VulnerabilityScanner")
        logger.setLevel(logging.DEBUG)

        # Avoid adding multiple handlers
        if logger.handlers:
            return logger

        # File handler
        log_file = os.path.join(
            self.log_dir,
            f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def info(self, message: str) -> None:
        """Log INFO level message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log WARNING level message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log ERROR level message."""
        self.logger.error(message)

    def debug(self, message: str) -> None:
        """Log DEBUG level message."""
        self.logger.debug(message)

    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self.logger
