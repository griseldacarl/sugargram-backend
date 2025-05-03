import json

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from torchvision.transforms import InterpolationMode

model = models.resnet101(weights=None)
model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(model.fc.in_features, 101))

model.load_state_dict(
    torch.load("static/food_resnet101_finetuned.pth", map_location=torch.device("cpu"))
)
model.eval()

with open("static/classes.json", "r") as file:
    classes = json.load(file)


def get_prediction(image):
    transfrom = transforms.Compose(
        [
            transforms.Resize((256, 256), interpolation=InterpolationMode.BILINEAR),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    img = Image.open(image)
    input_tensor = transfrom(img).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)

    _, predicted_class = torch.max(output, 1)

    return {
        "prediction": predicted_class.item(),
        "result": classes[predicted_class.item()]["class"],
    }
