from enum import Enum

class Taxon(Enum):
  PHYLUM = 'Phylum'
  CLASS = 'Class'
  ORDER = 'Order'
  FAMILY = 'Family'
  GENUS = 'Genus'
  SPECIES = 'Species'

TAXA = [Taxon.PHYLUM, Taxon.CLASS, Taxon.ORDER, Taxon.FAMILY, Taxon.GENUS, Taxon.SPECIES]