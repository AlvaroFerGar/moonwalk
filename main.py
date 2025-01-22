import sys
from moonkwalkui import MoonWalkUI
from PyQt5.QtWidgets import QApplication

def main(args):
    model_path='models/moondream-2b-int8.mf'
    if len(args) > 1:
        model_path = args[1]
    
    print(f"Using model path: {model_path}")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MoonWalkUI(model_path)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main(sys.argv)