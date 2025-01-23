import sys
from moonwalkcore import MoonWalkCore


def main(args):
    model_path='models/moondream-2b-int8.mf'
    if len(args) > 1:
        model_path = args[1]
    
    print(f"Using model path: {model_path}")
    

    core = MoonWalkCore()
    core.model_path=model_path
    core.load_model()

    while True:
        print("======================================================")
        print("\r\r\r\r")

        #Ask for image file
        image_path = input("Enter the path to the image file (or type 'exit' to quit): ").strip()

        #If exit->exit
        if image_path.lower() in ['exit', 'x']:
            print("Exiting the program.")
            break

        class_propmt = input("Enter the prompt for human/class detection (leave empty for 'humans'): ").strip()
        if not class_propmt:
            class_propmt = "humans"
        core.people_prompt = class_propmt

        subclass_propmt = input("Enter the prompt for kids/subclass detection (leave empty for 'kids'): ").strip()
        if not subclass_propmt:
            subclass_propmt = "kids"
        core.kids_prompt = subclass_propmt



        core.run_detection(image_path=image_path)


if __name__ == "__main__":
    main(sys.argv)