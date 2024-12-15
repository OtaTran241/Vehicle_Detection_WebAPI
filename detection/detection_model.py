import os
import uuid
from PIL import Image, ImageDraw, ImageFont
import torch
import torchvision.transforms as T
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from app.core.config import settings

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

num_classes_dict = {0: 'cars', 1: 'Bus', 2: 'Car', 3: 'Motorcycle', 4: 'Pickup', 5: 'Truck'}
color_dict = {'cars': (255, 0, 0), 
              'Bus': (0, 255, 0), 
              'Car': (0, 0, 255), 
              'Motorcycle': (255, 255, 0), 
              'Pickup': (255, 0, 255), 
              'Truck': (0, 255, 255)}

def get_model(num_classes, pretrained=True):
    """
    Get the Faster R-CNN model with the specified number of classes.

    Args:
    num_classes (int): The number of classes for the model.
    pretrained (bool): Whether to use a pretrained model.

    Returns:
    model: The Faster R-CNN model.
    """
    model = fasterrcnn_resnet50_fpn(pretrained=pretrained)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model

def load_model():
    """
    Load the vehicle detection model.

    Returns:
    model: The loaded model.
    """
    num_classes = len(num_classes_dict)
    model = get_model(num_classes, pretrained=False)
    model.load_state_dict(torch.load("detection/model/VehicleFasterRcnnModel.pth", map_location=device))
    model = model.to(device)
    model.eval()
    return model

def predict_image(model, image):
    """
    Run vehicle detection on an image.

    Args:
    model: The vehicle detection model.
    image (PIL.Image): The input image.

    Returns:
    str: The path to the annotated image.
    """
    transform = T.Compose([T.ToTensor()])
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        predictions = model(image_tensor)
    
    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)
    font = ImageFont.load_default()

    for box, label, score in zip(predictions[0]['boxes'], predictions[0]['labels'], predictions[0]['scores']): 
        if score > 0.5:
            box = box.tolist()
            class_name = num_classes_dict[label.item()]
            color = color_dict[class_name]
            draw.rectangle(((box[0], box[1]), (box[2], box[3])), outline=color, width=3)
            draw.text((box[0], box[1] - 10), f"{class_name}: {score:.2f}", fill=color, font=font)

    unique_filename = f"annotated_{uuid.uuid4()}.jpg"
    output_path = os.path.join(settings.TEMP_DIR, unique_filename)
    annotated_image.save(output_path)
    return output_path, predictions

def run_detection(file_path):
    """
    Run vehicle detection on an image file.

    Args:
    file_path (str): The path to the input image file.

    Returns:
    dict: A dictionary containing the output image path, predictions, and a success message.
    """
    image = Image.open(file_path).convert("RGB")
    model = load_model()
    output_image_path, predictions = predict_image(model, image)
    
    json_serializable_predictions = []
    for prediction in predictions:
        json_serializable_predictions.append({
            'boxes': prediction['boxes'].tolist(),  
            'labels': prediction['labels'].tolist(), 
            'scores': prediction['scores'].tolist()   
        })
    
    original_image_url = f"{os.path.basename(file_path)}"
    output_image_url = f"{os.path.basename(output_image_path)}"
    
    return {
        "original_image_url": original_image_url,
        "output_image_url": output_image_url,
        "predictions": json_serializable_predictions,
        "message": "Detection complete!"
    }