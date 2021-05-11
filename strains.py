import csv

from taxa import ORDERED_TAXA, Taxa

DATA_FILE_PATH = 'data/Data_file_for_mapping.csv'

TAXA_GETTERS = {
  Taxa.PHYLUM: lambda strain: strain.phylum,
  Taxa.CLASS: lambda strain: strain.class_,
  Taxa.ORDER: lambda strain: strain.order,
  Taxa.FAMILY: lambda strain: strain.family,
  Taxa.GENUS: lambda strain: strain.genus,
  Taxa.SPECIES: lambda strain: strain.species,
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
  
  def get_taxa_name(self, taxa):
    return TAXA_GETTERS[taxa](self)

def parse_taxa_name(name, prefix):
  if name == "na":
    return None
  
  return name[len(prefix):] if name.startswith(prefix) else name

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
  strains_index = {taxa:dict() for taxa in ORDERED_TAXA}

  for strain in strains:
    for taxa in ORDERED_TAXA:
      name = strain.get_taxa_name(taxa)
      if name is None:
        continue

      if name in strains_index[taxa]:
        strains_index[taxa][name].append(strain)
      else:
        strains_index[taxa][name] = [strain]

  return strains_index
