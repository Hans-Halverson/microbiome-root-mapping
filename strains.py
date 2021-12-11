import csv
from os import path
from microbiome import Microbiome

from taxa import TAXA, Taxon

ENDOSPHERE_DATA_FILE_PATH = path.join(path.dirname(__file__), 'resources', 'endosphere', 'data_file_for_mapping.csv')
RHIZOSPHERE_DATA_FILE_PATH = path.join(path.dirname(__file__), 'resources', 'rhizosphere', 'data_file_for_mapping.csv')
ASV_KEY = 'ASV'

TAXA_GETTERS = {
  Taxon.PHYLUM: lambda strain: strain.phylum,
  Taxon.CLASS: lambda strain: strain.class_,
  Taxon.ORDER: lambda strain: strain.order,
  Taxon.FAMILY: lambda strain: strain.family,
  Taxon.GENUS: lambda strain: strain.genus,
}

class Strain:
  def __init__(self, id, phylum, class_, order, family, genus, abundances):
    self.id = id
    self.phylum = phylum
    self.class_ = class_
    self.order = order
    self.family = family
    self.genus = genus
    self.abundances = abundances
  
  def get_taxon_name(self, taxon):
    return TAXA_GETTERS[taxon](self)

def parse_taxon_name(name, prefix):
  if name == "na":
    return None
  
  return name[len(prefix):] if name.startswith(prefix) else name

def parse_strains_files():
  endosphere_strains = parse_strains_file(ENDOSPHERE_DATA_FILE_PATH)
  rhizosphere_strains = parse_strains_file(RHIZOSPHERE_DATA_FILE_PATH)

  return { Microbiome.ENDOSPHERE: endosphere_strains, Microbiome.RHIZOSPHERE: rhizosphere_strains }

def parse_strains_file(file):
  with open(file) as data_file:
    reader = csv.reader(data_file)
    # Skip first row which contains column labels
    next(reader)

    strains = []
    for row in reader:
      phylum = parse_taxon_name(row[0], "p__")
      class_ = parse_taxon_name(row[1], "c__")
      order = parse_taxon_name(row[2], "o__")
      family = parse_taxon_name(row[3], "f__")
      genus = parse_taxon_name(row[4], "g__")
      id = row[5]
      abundances = [float(abundance) for abundance in row[6:]]

      strain = Strain(id, phylum, class_, order, family, genus, abundances)
      strains.append(strain)

    return strains

def build_strains_indices(all_strains):
  return { microbiome: build_strains_index(strains) for microbiome, strains in all_strains.items() }

def build_strains_index(strains):
  strains_index = { taxon:dict() for taxon in TAXA }
  strains_index[ASV_KEY] = dict()

  for strain in strains:
    for taxon in TAXA:
      name = strain.get_taxon_name(taxon)
      if name is None:
        continue

      if name in strains_index[taxon]:
        strains_index[taxon][name].append(strain)
      else:
        strains_index[taxon][name] = [strain]
    
    # Index by ASV id
    strains_index[ASV_KEY][strain.id] = [strain]

  return strains_index
