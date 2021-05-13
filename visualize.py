from PIL import Image, ImageDraw, ImageFont
from os import path

IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920

NUM_MASKS = 56

TEMPLATE_PATH = path.join(path.dirname(__file__), 'resources', 'Template.png')
TEMPLATE = Image.open(TEMPLATE_PATH, 'r')

ARIAL_FONT_PATH = path.join(path.dirname(__file__), 'resources', 'arial.ttf')
HIERARCHY_FONT = ImageFont.truetype(ARIAL_FONT_PATH, size=20)

def load_masks():
  masks = []
  for i in range(1, NUM_MASKS + 1):
    mask_path = path.join(path.dirname(__file__), 'resources', f'{i}_mask-01.png')
    masks.append(Image.open(mask_path))
  
  return masks

MASKS = load_masks()

def sum_strain_values(strains):
  sums = [0.0] * NUM_MASKS
  for strain in strains:
    for i, value in enumerate(strain.values):
      sums[i] += value
  
  return sums

def render_image(strains, hierarchy):
  values = sum_strain_values(strains)

  image = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 255, 255, 255))

  draw = ImageDraw.Draw(image)
  draw.text((10, 10), "  >  ".join(hierarchy), fill=(0, 0, 0, 255), font=HIERARCHY_FONT)

  for i, value in enumerate(values):
    if value != 0.0:
      image.alpha_composite(MASKS[i])

  image.alpha_composite(TEMPLATE)

  return image