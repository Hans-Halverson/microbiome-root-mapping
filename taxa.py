from enum import Enum

class Taxa(Enum):
  PHYLUM = 'Phylum'
  CLASS = 'Class'
  ORDER = 'Order'
  FAMILY = 'Family'
  GENUS = 'Genus'
  SPECIES = 'Species'

ORDERED_TAXA = [Taxa.PHYLUM, Taxa.CLASS, Taxa.ORDER, Taxa.FAMILY, Taxa.GENUS, Taxa.SPECIES]