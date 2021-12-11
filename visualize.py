from PIL import Image, ImageDraw, ImageFont
from os import path

from microbiome import Microbiome

IMAGE_HEIGHT = 1080
IMAGE_WIDTH = 1920

ENDOSPHERE_NUM_MASKS = 56
RHIZOSPHERE_NUM_MASKS = 62

ENDOSPHERE_TEMPLATE_PATH = path.join(path.dirname(__file__), 'resources', 'endosphere', 'template.png')
RHIZOSPHERE_TEMPLATE_PATH = path.join(path.dirname(__file__), 'resources', 'rhizosphere', 'template.png')
ENDOSPHERE_TEMPLATE = Image.open(ENDOSPHERE_TEMPLATE_PATH, 'r')
RHIZOSPHERE_TEMPLATE = Image.open(RHIZOSPHERE_TEMPLATE_PATH, 'r')

ARIAL_FONT_PATH = path.join(path.dirname(__file__), 'resources', 'arial.ttf')
HIERARCHY_FONT = ImageFont.truetype(ARIAL_FONT_PATH, size=20)

COLOR_IMAGE = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 0, 0))
WHITE_IMAGE = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 255, 255, 255))

def num_masks(microbiome):
  if microbiome == Microbiome.ENDOSPHERE:
    return ENDOSPHERE_NUM_MASKS
  else:
    return RHIZOSPHERE_NUM_MASKS

def load_masks(microbiome):
  directory = 'endosphere' if microbiome == Microbiome.ENDOSPHERE else 'rhizosphere'
  masks = []
  for i in range(1, num_masks(microbiome) + 1):
    mask_path = path.join(path.dirname(__file__), 'resources', directory, f'{i}_mask-01.png')
    mask_image = Image.open(mask_path)
    # Only alpha channel of masks are used
    mask = mask_image.getchannel(3)
    masks.append(mask)
  
  return masks

ENDOSPHERE_MASKS = load_masks(Microbiome.ENDOSPHERE)
RHIZOSPHERE_MASKS = load_masks(Microbiome.RHIZOSPHERE)

def average_strain_abundances(microbiome, strains):
  if len(strains) == 0:
    return []

  sums = [0.0] * num_masks(microbiome)
  for strain in strains:
    for i, abundance in enumerate(strain.abundances):
      sums[i] += abundance
  
  averages = []
  for sum in sums:
    averages.append(sum / len(strains))
  
  return averages

def render_image(strains, microbiome, hierarchy, color, scale):
  abundances = average_strain_abundances(microbiome, strains)

  template, masks = (ENDOSPHERE_TEMPLATE, ENDOSPHERE_MASKS) if microbiome == Microbiome.ENDOSPHERE else (RHIZOSPHERE_TEMPLATE, RHIZOSPHERE_MASKS)

  color_image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), color)
  image = WHITE_IMAGE.copy()

  draw = ImageDraw.Draw(image)
  draw.text((10, 10), "  >  ".join(hierarchy), fill=(0, 0, 0, 255), font=HIERARCHY_FONT)

  for i, abundance in enumerate(abundances):
    if abundance != 0.0:
      scaled_abundance = min(abundance * scale, 1.0)
      alpha_mask = masks[i].point(lambda x: x * scaled_abundance)

      layer = color_image.copy()
      layer.putalpha(alpha_mask)

      image.alpha_composite(layer)

  image.alpha_composite(template)

  return image