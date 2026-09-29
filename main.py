"""
SHARTNOMA GENERATOR - Main Application Entry Point
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

from config import (
    APP_NAME, APP_VERSION, LOG_FILE, LOG_LEVEL,
    APP_DATA_DIR, DEBUG, DATE_FORMAT
)
from main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ShartnomaApplication(QApplication):
    """Main application class"""

    def __init__(self, argv):
        """Initialize application"""
        super().__init__(argv)
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)

        # Initialize UI
        self.main_window = None
        self.init_app()

    def init_app(self):
        """Initialize application"""
        try:
            logger.info(f"Starting {APP_NAME} v{APP_VERSION}")

            # Check required directories
            self.check_directories()

            # Create main window
            self.main_window = MainWindow()
            self.main_window.show()

            logger.info("Application started successfully")

        except Exception as e:
            logger.error(f"Error initializing application: {e}")
            QMessageBox.critical(None, "Xato", f"Dastur ishga tushirganda xato: {str(e)}")
            sys.exit(1)

    @staticmethod
    def check_directories():
        """Check and create required directories"""
        required_dirs = [
            APP_DATA_DIR,
            APP_DATA_DIR / "Templates",
            APP_DATA_DIR / "Contracts",
            APP_DATA_DIR / "Settings",
            APP_DATA_DIR / "logs"
        ]

        for directory in required_dirs:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directory verified: {directory}")
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")
                raise

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        QMessageBox.critical(
            self.main_window,
            "Dastur xatosi",
            f"Kutilmagan xato yuz berdi:\n{exc_type.__name__}: {exc_value}"
        )


def main():
    """Main application entry point"""
    try:
        # Create application
        app = ShartnomaApplication(sys.argv)

        # Set up exception handler
        sys.excepthook = app.handle_exception

        logger.info("=" * 60)
        logger.info(f"{APP_NAME} v{APP_VERSION}")
        logger.info(f"Start time: {Path(LOG_FILE).read_text().split()[-1] if Path(LOG_FILE).exists() else 'unknown'}")
        logger.info("=" * 60)

        # Run application
        exit_code = app.exec()

        logger.info(f"Application closed with exit code: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
