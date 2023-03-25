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

#added gridsize, which is a tuple (x, y) for how large the grid should be
def grid(FS, gridsize):
    images = []
    for y in range(0, gridsize[1]):
        for x in range(0, gridsize[0]):
            image = (read_image(determine_image((x, y), FS)))
            images.append(image)
    
    Grid = make_grid(images, nrow=gridsize[0], padding=25)
    img = torchvision.transforms.ToPILImage()(Grid)
    return img
