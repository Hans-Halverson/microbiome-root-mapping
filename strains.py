import csv
from os import path

from taxa import TAXA, Taxon

DATA_FILE_PATH = path.join(path.dirname(__file__), 'resources', 'Data_file_for_mapping.csv')
ASV_KEY = 'ASV'

TAXA_GETTERS = {
  Taxon.PHYLUM: lambda strain: strain.phylum,
  Taxon.CLASS: lambda strain: strain.class_,
  Taxon.ORDER: lambda strain: strain.order,
  Taxon.FAMILY: lambda strain: strain.family,
  Taxon.GENUS: lambda strain: strain.genus,
  Taxon.SPECIES: lambda strain: strain.species,
}

class Strain:
  def __init__(self, id, phylum, class_, order, family, genus, species, values):
    self.id = id
    self.phylum = phylum
    self.class_ = class_
    self.order = order
    self.family = family
    self.genus = genus
    self.species = species
    self.values = values
  
  def get_taxon_name(self, taxa):
    return TAXA_GETTERS[taxa](self)

def parse_taxa_name(name, prefix):
  if name == "na":
    return None
  
  return name[len(prefix):] if name.startswith(prefix) else name

import numpy as np
from matplotlib import pyplot as plt

def parse_strains_file():
  with open(DATA_FILE_PATH) as data_file:
    reader = csv.reader(data_file)
    # Skip first row which contains column labels
    next(reader)

    strains = []
    for row in reader:
      phylum = parse_taxa_name(row[0], "p__")
      class_ = parse_taxa_name(row[1], "c__")
      order = parse_taxa_name(row[2], "o__")
      family = parse_taxa_name(row[3], "f__")
      genus = parse_taxa_name(row[4], "g__")
      species = parse_taxa_name(row[5], "s__")
      id = row[6]
      values = [float(value) for value in row[7:]]

      strain = Strain(id, phylum, class_, order, family, genus, species, values)
      strains.append(strain)

    return strains

def build_strains_index(strains):
  strains_index = {taxa:dict() for taxa in TAXA}
  strains_index[ASV_KEY] = dict()

  for strain in strains:
    for taxa in TAXA:
      name = strain.get_taxon_name(taxa)
      if name is None:
        continue

      if name in strains_index[taxa]:
        strains_index[taxa][name].append(strain)
      else:
        strains_index[taxa][name] = [strain]
    
    # Index by ASV id
    strains_index[ASV_KEY][strain.id] = [strain]

  return strains_index
