from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QFileDialog, QTextEdit, QGroupBox, QFormLayout, QProgressBar)
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

        config_group = QGroupBox("Model Data")
        config_layout = QFormLayout()

        # Model Name como label
        model_label = QLabel("Model:")
        model_name_display = QLabel(self.core.model_name)
        model_name_display.setStyleSheet("font-weight: bold;")
        config_layout.addRow(model_label, model_name_display)

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

        select_button = QPushButton("Select Image")
        select_button.clicked.connect(self.select_image)
        main_layout.addWidget(select_button)

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


        self.run_button = QPushButton("Run Detection")
        self.run_button.clicked.connect(self.run_detection)
        main_layout.addWidget(self.run_button)

        # Create horizontal layout for count labels
        counts_layout = QHBoxLayout()
        counts_layout.addStretch()
        # Class elements count label
        class_label = QLabel("Number of class elements:")
        class_label.setStyleSheet("color: blue;")
        self.class_count_label = QLabel("0")
        self.class_count_label.setStyleSheet("color: blue; font-size: 14pt; font-weight: bold;")

        # Add class labels to layout
        counts_layout.addWidget(class_label)
        counts_layout.addWidget(self.class_count_label)

        # Add some spacing between the labels
        counts_layout.addSpacing(20)

        # Subclass elements count label
        subclass_label = QLabel("Number of subclass elements:")
        subclass_label.setStyleSheet("color: rgb(153,204,255);")
        self.subclass_count_label = QLabel("0")
        self.subclass_count_label.setStyleSheet("color: rgb(153,204,255); font-size: 14pt; font-weight: bold;")

        # Add subclass labels to layout
        counts_layout.addWidget(subclass_label)
        counts_layout.addWidget(self.subclass_count_label)

        # Add stretch to push labels to the left
        counts_layout.addStretch()

        # Add the counts layout to main layout
        main_layout.addLayout(counts_layout)

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
            self.class_count_label.setText(str(0))
            self.class_count_label.setText(str(0))

    def validate_parameters(self):
        """Validate all parameters before running detection"""
        try:
            # Validate max dimension is a number
            max_dim = int(self.max_dimension_input.text())
            if max_dim <= 0:
                raise ValueError("Max dimension must be positive")

            # Validate prompt names are not empty
            if not self.people_prompt_input.text().strip():
                raise ValueError("People prompt cannot be empty")
            if not self.kids_prompt_input.text().strip():
                raise ValueError("Kids prompt cannot be empty")

            # Update core parameters
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
            self.run_button.setText('WORKING...')
            QApplication.processEvents()
            result_path, n_people, n_kids = self.core.run_detection(self.current_image_path)
            self.run_button.setText('Run Detection')
            self.class_count_label.setText(str(n_people))
            self.subclass_count_label.setText(str(n_kids))
            # Assuming run_detection returns the path to the result image
            if result_path:
                self.load_and_display_image(result_path, self.output_image_label)
        except Exception as e:
            pass