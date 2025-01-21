import sys
from moonkwalkui import MoonWalkUI
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MoonWalkUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()