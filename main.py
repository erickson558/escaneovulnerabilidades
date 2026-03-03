"""Main entry point for Vulnerability Scanner application."""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from src import __version__, __description__
from src.config import ConfigManager
from src.frontend.app import VulnerabilityScannerApp
from src.utils.helpers import detect_os


def main():
    """Main entry point for the application."""
    config = ConfigManager()
    
    # Check if running on headless Linux system
    os_name = detect_os()
    if os_name == 'Linux' and not os.environ.get('DISPLAY'):
        print(f"{__description__} v{__version__}")
        print("GUI mode not available on headless system")
        return

    # Launch GUI application
    app = VulnerabilityScannerApp(version=__version__)
    app.mainloop()


if __name__ == '__main__':
    main()
