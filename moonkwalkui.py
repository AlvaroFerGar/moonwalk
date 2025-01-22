from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QFileDialog, QTextEdit, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from moonwalkcore import MoonWalkCore

class MoonWalkUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.core = MoonWalkCore()
        self.core.load_model()
        self.current_image_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('MoonWalk')
        self.setMinimumSize(800, 800)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Configuration Group
        config_group = QGroupBox("Model Configuration")
        config_layout = QFormLayout()

        # Model Path
        self.model_path_input = QLineEdit(self.core.model_path)
        config_layout.addRow("Model Path:", self.model_path_input)

        # Model Name
        self.model_name_input = QLineEdit(self.core.model_name)
        config_layout.addRow("Model Name:", self.model_name_input)

        # Max Dimension
        self.max_dimension_input = QLineEdit(str(self.core.max_dimension))
        config_layout.addRow("Max Dimension:", self.max_dimension_input)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Prompts Group
        prompts_group = QGroupBox("Detection Prompts")
        prompts_layout = QVBoxLayout()

        # Horizontal layout for people and kids prompts
        prompts_horizontal = QHBoxLayout()

        # People Prompt
        people_layout = QVBoxLayout()
        people_layout.addWidget(QLabel("Class Prompt:"))
        self.people_prompt_input = QLineEdit(self.core.people_prompt)
        people_layout.addWidget(self.people_prompt_input)
        prompts_horizontal.addLayout(people_layout)

        # Kids Prompt
        kids_layout = QVBoxLayout()
        kids_layout.addWidget(QLabel("Sub-class Prompt:"))
        self.kids_prompt_input = QLineEdit(self.core.kids_prompt)
        kids_layout.addWidget(self.kids_prompt_input)
        prompts_horizontal.addLayout(kids_layout)

        prompts_layout.addLayout(prompts_horizontal)
        prompts_group.setLayout(prompts_layout)
        main_layout.addWidget(prompts_group)

        # Images Section
        images_layout = QHBoxLayout()

        # Input Image
        input_image_group = QGroupBox("Input Image")
        input_layout = QVBoxLayout()
        self.input_image_label = QLabel()
        self.input_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_image_label.setMinimumSize(300, 300)
        input_layout.addWidget(self.input_image_label)
        input_image_group.setLayout(input_layout)
        images_layout.addWidget(input_image_group)

        # Output Image
        output_image_group = QGroupBox("Result Image")
        output_layout = QVBoxLayout()
        self.output_image_label = QLabel()
        self.output_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_image_label.setMinimumSize(300, 300)
        output_layout.addWidget(self.output_image_label)
        output_image_group.setLayout(output_layout)
        images_layout.addWidget(output_image_group)

        main_layout.addLayout(images_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        select_button = QPushButton("Select Image")
        select_button.clicked.connect(self.select_image)
        run_button = QPushButton("Run Detection")
        run_button.clicked.connect(self.run_detection)
        
        buttons_layout.addWidget(select_button)
        buttons_layout.addWidget(run_button)
        main_layout.addLayout(buttons_layout)

    def load_and_display_image(self, image_path, label):
        """Load and display an image in the specified label"""
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale pixmap to fit in label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                label.setPixmap(scaled_pixmap)
        else:
            label.clear()

    def validate_parameters(self):
        """Validate all parameters before running detection"""
        try:
            # Validate max dimension is a number
            max_dim = int(self.max_dimension_input.text())
            if max_dim <= 0:
                raise ValueError("Max dimension must be positive")

            # Validate paths and names are not empty
            if not self.model_path_input.text().strip():
                raise ValueError("Model path cannot be empty")
            if not self.model_name_input.text().strip():
                raise ValueError("Model name cannot be empty")
            if not self.people_prompt_input.text().strip():
                raise ValueError("People prompt cannot be empty")
            if not self.kids_prompt_input.text().strip():
                raise ValueError("Kids prompt cannot be empty")

            # Update core parameters
            self.core.model_path = self.model_path_input.text()
            self.core.model_name = self.model_name_input.text()
            self.core.max_dimension = max_dim
            self.core.people_prompt = self.people_prompt_input.text()
            self.core.kids_prompt = self.kids_prompt_input.text()

            return True

        except ValueError as e:
            return False

    def select_image(self):
        """Open file dialog to select an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        
        if file_path:
            if self.current_image_path != file_path:
                self.load_and_display_image("", self.output_image_label)
            self.current_image_path = file_path
            self.load_and_display_image(file_path, self.input_image_label)


    def run_detection(self):
        """Run detection with current parameters and selected image"""
        if not self.current_image_path or not self.validate_parameters():
            return

        try:
            result_path = self.core.run_detection(self.current_image_path)
            # Assuming run_detection returns the path to the result image
            if result_path:
                self.load_and_display_image(result_path, self.output_image_label)
        except Exception as e:
            pass