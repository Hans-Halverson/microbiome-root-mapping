from PIL import Image, ImageDraw, ImageFont
from os import path

IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920

NUM_MASKS = 56

TEMPLATE_PATH = path.join(path.dirname(__file__), 'resources', 'Template.png')
TEMPLATE = Image.open(TEMPLATE_PATH, 'r')

ARIAL_FONT_PATH = path.join(path.dirname(__file__), 'resources', 'arial.ttf')
HIERARCHY_FONT = ImageFont.truetype(ARIAL_FONT_PATH, size=20)

COLOR_IMAGE = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 0, 0))
WHITE_IMAGE = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 255, 255, 255))

def load_masks():
  masks = []
  for i in range(1, NUM_MASKS + 1):
    mask_path = path.join(path.dirname(__file__), 'resources', f'{i}_mask-01.png')
    mask_image = Image.open(mask_path)
    # Only alpha channel of masks are used
    mask = mask_image.getchannel(3)
    masks.append(mask)
  
  return masks

MASKS = load_masks()

def sum_strain_values(strains):
  sums = [0.0] * NUM_MASKS
  for strain in strains:
    for i, value in enumerate(strain.values):
      sums[i] += value
  
  return sums

def render_image(strains, hierarchy, color):
  values = sum_strain_values(strains)

  color_image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), color)
  image = WHITE_IMAGE.copy()

  draw = ImageDraw.Draw(image)
  draw.text((10, 10), "  >  ".join(hierarchy), fill=(0, 0, 0, 255), font=HIERARCHY_FONT)

  for i, value in enumerate(values):
    if value != 0.0:
      # Normalize value to be on scale from 0.0 to 1.0, since highest value is approximately 0.2
      norm_value = min(value * 5, 1.0)

      scaled_value = norm_value
      alpha_mask = MASKS[i].point(lambda x: x * scaled_value)

      layer = color_image.copy()
      layer.putalpha(alpha_mask)

      image.alpha_composite(layer)

  image.alpha_composite(TEMPLATE)

  return image