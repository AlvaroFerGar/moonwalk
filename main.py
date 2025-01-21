import os
import moondream as md
from PIL import Image
import time
from rich.console import Console
from utils import detection_routine, filter_overlapping_detections, draw_bboxes

console = Console()
# Initialize with local model path. Can also read .mf.gz files, but we recommend decompressing
# up-front to avoid decompression overhead every time the model is initialized.
model_path="models"
model_name = "moondream-2b-int8.mf"
max_dimension = 248
people_prompt="humans"
kids_prompt="kids"
crosswalk_prompt="crosswalk"


console.print(f"Loading model {model_name}...", style="bold")
start_time = time.time()
model = md.vl(model=model_path+"/" + model_name)
console.print(f"Model {model_name} loaded in {time.time()-start_time:.2f} seconds.", style="bold green")


while True:
    console.print("======================================================", style="bold white")
    print("\r\r\r\r")

    #Ask for image file
    image_path = input("Enter the path to the image file (or type 'exit' to quit): ").strip()

    #If exit->exit
    if image_path.lower() in ['exit', 'x']:
        print("Exiting the program.")
        break

    # If file doesnt exit, new iteration
    if not os.path.isfile(image_path):
        print("The file does not exist. Please try again.")
        continue

    # Check if valid image
    try:
        with Image.open(image_path) as img:
            img.verify()
        print("The file is a valid image.")
    except (IOError, SyntaxError):
        print("The file is not a valid image. Please try again.")

    # Resize (for better perfomance) and encode image
    print("Encoding image...")
    start_time = time.time()
    orig_image = Image.open(image_path)

    original_width, original_height = orig_image.size

    # Resize. Max dimension=max dimension and keep original aspect ratio 
    if original_width > original_height:
        new_width = max_dimension
        new_height = int((new_width / original_width) * original_height)
    else:
        new_height = max_dimension
        new_width = int((new_height / original_height) * original_width)   
    image = orig_image.resize((new_width, new_height))
    
    encoded_image = model.encode_image(image)
    print(f"Encoded in {time.time()-start_time:.2f} seconds.")
    print("\r\r")


    ## Detection

    #Reset variables
    n_orig_people=0
    n_people=0
    n_adults=0
    n_kids=0

    result_people=[]
    result_kids=[]
    result_adults=[]
    result_crosswalk=[]

    
    result_people = detection_routine(model, image, people_prompt, time)
    n_orig_people=len(result_people['objects'])
    console.print(f"Found {n_orig_people} {people_prompt}", style="bold green")

    print("\r\r")

    if n_orig_people>0:

        result_kids = detection_routine(model, image, kids_prompt, time)
        n_kids=len(result_kids['objects'])
        console.print(f"Found {n_kids} {kids_prompt}", style="bold green")

        img_width, img_height = orig_image.size

        # Filtrar las detecciones solapadas
        result_adults = filter_overlapping_detections(
            result_people, 
            result_kids,
            iou_threshold=0.5,
            img_width=img_width,
            img_height=img_height
        )

        n_adults=len(result_adults['objects'])
        n_people=n_adults+n_kids
        if(n_people>n_orig_people):
            console.print(f"Detected {n_people-n_orig_people} new humans")
        console.print(f"Of the {n_people} humans, {n_kids} seem to be children", style="bold blue")
        print("\r\r")

    else:

        crosswalk_prompt="crosswalk"
        result_crosswalk = detection_routine(model, image, crosswalk_prompt, time)
        #print("result:")
        #print(result_crosswalk)
        if len(result_crosswalk['objects'])==0:
            console.print("There isn't even a crosswalk in the image provided!!", style="yellow bold")
        else:
            print("At least there is a crosswalk in the image provided...")
        print("\r\r")

    # Dibujar los bounding boxes filtrados
    result_image=orig_image
    if(n_people>0):
        result_image = draw_bboxes(
            orig_image,
            [result_adults, result_kids],
            colors=[(0,0,255), (153,204,255)]
        )


    output_path = f"{os.path.splitext(image_path)[0]}_moonwalked{os.path.splitext(image_path)[1]}"
    result_image.save(output_path)
    print(f"Result image saved to {output_path}")
    console.print("Adults' bboxes: blue", style="bold blue")
    console.print("Children's bboxes: lightblue", style="bold rgb(153,204,255)")