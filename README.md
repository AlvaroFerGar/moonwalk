# 🚶 🌔 Moonwalk 🌖 🚶

**Moonwalk** is a small PyQt application for testing Moondream models. Its original purpose is to detect adults and kids crossing crosswalks. However, since Moondream is a VLM(Vision Language Model), it can be reconfigured to detect any class-subclass elements (e.g., animal/tiger, fruit/apple).

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/AlvaroFerGar/moonwalk.git
    cd moonwalk
    ```
2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Download your favourite moondream model a place it on the models folder. 
5. Run the application:
    ```sh
    python main.py path/to/my/awesomemodel.mf
    ```
    If you don't especify any path as an argument it will automatically look for a moondream-2b-int8.mf in the models folder
    ```sh
    python main.py 
    ```

7. Use the GUI to select an image, configure detection parameters, and run the detection. After a few seconds the result will appear on screen.
   ![screenshot](assets/screenshot.png)
   Output images will be saved on the result_images folder
  
## Project Structure

```
moonwalk/
├── assets/
├── models/
│   ├── download_moondream_to_this_folder.txt
├── newenv/
├── result_images/
│   └── resultimages_will_be_saved_here.txt
├── main.py
├── moonkwalkui.py
├── moonwalkcore.py
├── utils.py
├── requirements.txt
└── .gitignore
```

main.py: Entry point of the application.

moonkwalkui.py:Contains the GUI implementation using PyQt5.

moonwalkcore.py: Core logic for loading the model and running detection.

utils.py: Utility functions for detection and image processing.

requirements.txt: List of dependencies required to run the application.
models

