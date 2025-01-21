import os
import moondream as md
from PIL import Image
from PIL import ImageDraw
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def calculate_iou(box1, box2, img_width, img_height):
    """
    Calcula el IoU (Intersection over Union) entre dos bounding boxes.
    Las coordenadas deben estar normalizadas (0-1).
    """
    # Convertir coordenadas normalizadas a píxeles
    box1_pixels = {
        'x_min': box1['x_min'] * img_width,
        'y_min': box1['y_min'] * img_height,
        'x_max': box1['x_max'] * img_width,
        'y_max': box1['y_max'] * img_height
    }
    
    box2_pixels = {
        'x_min': box2['x_min'] * img_width,
        'y_min': box2['y_min'] * img_height,
        'x_max': box2['x_max'] * img_width,
        'y_max': box2['y_max'] * img_height
    }
    
    # Calcular coordenadas de la intersección
    x_min_inter = max(box1_pixels['x_min'], box2_pixels['x_min'])
    y_min_inter = max(box1_pixels['y_min'], box2_pixels['y_min'])
    x_max_inter = min(box1_pixels['x_max'], box2_pixels['x_max'])
    y_max_inter = min(box1_pixels['y_max'], box2_pixels['y_max'])
    
    # Calcular área de intersección
    if x_min_inter < x_max_inter and y_min_inter < y_max_inter:
        intersection = (x_max_inter - x_min_inter) * (y_max_inter - y_min_inter)
    else:
        return 0.0
    
    # Calcular áreas de cada box
    box1_area = (box1_pixels['x_max'] - box1_pixels['x_min']) * (box1_pixels['y_max'] - box1_pixels['y_min'])
    box2_area = (box2_pixels['x_max'] - box2_pixels['x_min']) * (box2_pixels['y_max'] - box2_pixels['y_min'])
    
    # Calcular unión
    union = box1_area + box2_area - intersection
    
    # Calcular IoU
    return intersection / union if union > 0 else 0.0

def filter_overlapping_detections(adults_result, kids_result, iou_threshold=0.5, img_width=None, img_height=None):
    """
    Filtra las detecciones de adultos que tienen un alto solapamiento con las detecciones de niños.
    
    Args:
    adults_result: Diccionario con las detecciones de adultos
    kids_result: Diccionario con las detecciones de niños
    iou_threshold: Umbral de IoU para considerar que hay solapamiento (default: 0.5)
    img_width: Ancho de la imagen en píxeles
    img_height: Alto de la imagen en píxeles
    
    Returns:
    Diccionario con las detecciones de adultos filtradas
    """
    filtered_adults = {'objects': []}
    
    # Copiar todos los campos excepto 'objects'
    for key in adults_result:
        if key != 'objects':
            filtered_adults[key] = adults_result[key]
    
    # Para cada detección de adulto
    for adult_box in adults_result['objects']:
        should_keep = True
        
        # Comparar con cada detección de niño
        for kid_box in kids_result['objects']:
            iou = calculate_iou(adult_box, kid_box, img_width, img_height)
            
            # Si el IoU es mayor que el umbral, no incluir esta detección de adulto
            if iou > iou_threshold:
                should_keep = False
                break
        
        # Si no hay solapamiento significativo con ningún niño, mantener la detección
        if should_keep:
            filtered_adults['objects'].append(adult_box)
    
    return filtered_adults

def draw_bboxes(image, detections_list, colors=None):
    """
    Dibuja múltiples grupos de bounding boxes sobre una imagen.
    Args:
    image: PIL Image o ruta a la imagen
    detections_list: Lista de diccionarios con detecciones
    colors: Lista de colores RGB para cada grupo de detecciones
    Returns:
    PIL Image con todos los bboxes dibujados
    """
    # Crear una copia para no modificar la original
    image_with_boxes = image.copy()
    draw = ImageDraw.Draw(image_with_boxes)
    
    # Obtener dimensiones de la imagen
    img_width, img_height = image.size
    
    # Si no se especifican colores, usar rojo por defecto
    if colors is None:
        colors = [(255, 0, 0)] * len(detections_list)
    
    # Dibujar cada grupo de bboxes con su color correspondiente
    for detections, color in zip(detections_list, colors):
        for obj in detections['objects']:
            # Convertir coordenadas normalizadas a píxeles
            x_min = obj['x_min'] * img_width
            y_min = obj['y_min'] * img_height
            x_max = obj['x_max'] * img_width
            y_max = obj['y_max'] * img_height
            
            # Dibujar el rectángulo
            draw.rectangle(
                [(x_min, y_min), (x_max, y_max)],
                outline=color,
                width=2
            )
    
    return image_with_boxes

console = Console()
# Initialize with local model path. Can also read .mf.gz files, but we recommend decompressing
# up-front to avoid decompression overhead every time the model is initialized.
model_name = "moondream-2b-int8.mf.gz"
console.print(f"Loading model {model_name}...", style="bold")
start_time = time.time()
model = md.vl(model="models/" + model_name)
console.print(f"Model {model_name} loaded in {time.time()-start_time:.2f} seconds.", style="bold green")




while True:
    console.print("======================================================", style="bold white")
    #console.print(f"Loading model {model_name}...", style="bold blue")
    print("\r\r\r\r")

    image_path = input("Enter the path to the image file (or type 'exit' to quit): ").strip()

    # Check for exit condition
    if image_path.lower() in ['exit', 'x']:
        print("Exiting the program.")
        break

    # Check if the file exists
    if not os.path.isfile(image_path):
        print("The file does not exist. Please try again.")
        continue

    # Check if it's a valid image
    try:
        with Image.open(image_path) as img:
            img.verify()  # Check if it is an image
        print("The file is a valid image.")
    except (IOError, SyntaxError):
        print("The file is not a valid image. Please try again.")

    # Load and process image
    print("Encoding image...")
    start_time = time.time()
    orig_image = Image.open(image_path)

    # Obtener las dimensiones originales
    original_width, original_height = orig_image.size

    # Calcular el nuevo tamaño manteniendo el aspecto
    max_dimension = 248
    if original_width > original_height:
        new_width = max_dimension
        new_height = int((new_width / original_width) * original_height)
    else:
        new_height = max_dimension
        new_width = int((new_height / original_height) * original_width)

    # Redimensionar la imagen
    image = orig_image.resize((new_width, new_height))
    encoded_image = model.encode_image(image)
    print(f"Encoded in {time.time()-start_time:.2f} seconds.")
    print("\r\r")

    print("Detecting...")
    start_time = time.time()
    whatiwant="humans"

    result_people=[]
    result_kids=[]
    result_crosswalk=[]

    result_people = model.detect(image, whatiwant)
    #print("result:")
    #print(result_adults)
    console.print(f"Found {len(result_people['objects'])} {whatiwant}", style="bold green")
    print(f"Detected in {time.time()-start_time:.2f} seconds.")
    print("\r\r")

    if len(result_people['objects'])>0:
        print("Detecting...")
        start_time = time.time()
        whatiwant="kids"
        result_kids = model.detect(image, whatiwant)
        #print("result:")
        #print(result_kids)
        console.print(f"Found {len(result_kids['objects'])} {whatiwant}", style="bold green")
        print(f"Detected in {time.time()-start_time:.2f} seconds.")
        

        img_width, img_height = orig_image.size

        # Filtrar las detecciones solapadas
        filtered_adults_result = filter_overlapping_detections(
            result_people, 
            result_kids,
            iou_threshold=0.5,
            img_width=img_width,
            img_height=img_height
        )

        n_people=len(filtered_adults_result['objects'])+len(result_kids['objects'])
        if(len(filtered_adults_result['objects'])+len(result_kids['objects'])>len(result_people['objects'])):
            console.print(f"Detected {len(filtered_adults_result['objects'])+len(result_kids['objects'])-len(result_people['objects'])} new humans")
        console.print(f"Of the {n_people} humans, {len(result_kids['objects'])} seem to be children", style="bold blue")
        print("\r\r")

    if len(result_people['objects'])==0:
        print("Detecting...")
        start_time = time.time()
        whatiwant="crosswalk"
        result_crosswalk = model.detect(image, whatiwant)
        #print("result:")
        #print(result_crosswalk)
        if len(result_crosswalk['objects'])==0:
            console.print("There isn't even a crosswalk in the image provided!!", style="yellow bold")
        else:
            print("At least there is a crosswalk in the image provided...")
        print("\r\r")






    # Dibujar los bounding boxes filtrados
    result_image=orig_image
    if(len(filtered_adults_result)>0 | len(result_kids)>0):
        result_image = draw_bboxes(
            orig_image,
            [filtered_adults_result, result_kids],
            colors=[(0,0,255), (153,204,255)]
        )


    output_path = f"{os.path.splitext(image_path)[0]}_moonwalked{os.path.splitext(image_path)[1]}"
    result_image.save(output_path)
    print(f"Result image saved to {output_path}")
    console.print("Adults' bboxes: blue", style="bold blue")
    console.print("Children's bboxes: lightblue", style="bold rgb(153,204,255)")

