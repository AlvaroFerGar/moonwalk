from moonwalkcore import MoonWalkCore

if __name__ == "__main__":

    core = MoonWalkCore()
    core.load_model()

    while(True):
        image_path = input("Enter the path to the image file (or type 'exit' to quit): ").strip()
        
        if image_path.lower() in ['exit', 'x']:
            print("Exiting the program.")
            break
        
        core.run_detection(image_path)    

