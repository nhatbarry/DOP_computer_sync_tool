"""
DOP Computer Sync Tool
Main Application Entry Point

Refactored to use PyQt5 with MVC Architecture
Version: 2.0.0
"""

import sys
from PyQt5.QtWidgets import QApplication
from controllers import MainController


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("DOP Computer Sync Tool")
    app.setOrganizationName("DOP")
    
    controller = MainController()
    
    controller.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

