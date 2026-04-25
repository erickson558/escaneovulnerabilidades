"""Configuration module for Vulnerability Scanner.

This module handles loading, saving, and managing application configuration
from the config.json file.
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Manage application configuration."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "NVD_API_KEY": "",
        "window": {
            "width": 800,
            "height": 780      # altura extra para la fila de idioma/donación
        },
        "auto_start": False,
        "auto_close_enabled": False,
        "auto_close_seconds": 60,
        "pdf_folder": "",
        "language": "es"       # código de idioma activo: 'es' o 'en'
    }

    def __init__(self, config_file: str = "config.json"):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration JSON file.
        """
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default.
        
        Returns:
            Configuration dictionary.
        """
        if not os.path.exists(self.config_file):
            self._save_config(self.DEFAULT_CONFIG.copy())
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            config = self.DEFAULT_CONFIG.copy()

        # Ensure all default keys exist
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    config[key].setdefault(sub_key, sub_value)

        return config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save.
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def save(self) -> None:
        """Save current configuration to file."""
        self._save_config(self.config)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key.
            value: Value to set.
        """
        self.config[key] = value

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary notation."""
        return self.config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using dictionary notation."""
        self.config[key] = value
