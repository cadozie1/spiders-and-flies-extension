import torch
import torchvision
from torchvision.io import read_image
from torchvision.utils import make_grid

def determine_image(coordinates, FS):
    flies = FS[0]
    spiders = FS[1]

    if coordinates in spiders:
        if (spiders[0] == spiders[1]):
            return "spider2.png"
        else:
            return "spider.png"
    elif coordinates in flies:
        return "fly.png"
    else:
        return "white.png"

def grid(FS):
    images = []
    for y in range(0, 10):
        for x in range(0, 10):
            image = (read_image(determine_image((x, y), FS)))
            images.append(image)
    
    Grid = make_grid(images, nrow=10, padding=25)
    img = torchvision.transforms.ToPILImage()(Grid)
    return img
