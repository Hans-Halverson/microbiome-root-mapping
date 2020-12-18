# Dictionary of organism id to dictionary of location name to value
location_data = dict()

# Set of all organism ids
organism_ids = set()

# List of all location names
location_names = []

# All taxonomic ranks in order
TAX_RANK_NAMES = ['Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']

# Dictionary of tax rank name to dictionary of name to set of organism ids with tax rank of that name
tax_ranks = {rank:dict() for rank in TAX_RANK_NAMES}

# Ingest and clean table of organism id to values at locations
def read_raw_location_values_file():
  with open('data/rootarch_all_ASV.tsv') as f:
    lines = f.readlines()
    table = [line.split() for line in lines]
    # Ignore first six columns in first row
    global location_names
    location_names = table[0][6:]

    for row in table[1:]:
      organism_id = row[0]
      organism_ids.add(organism_id)

      # Ignore first seven columns in later rows (first column had a missing entry at (0, 0))
      locations = dict()
      for i, val in enumerate(row[7:]):
        locations[location_names[i]] = float(val)
      location_data[organism_id] = locations

# Normalize data (divide each value by the total sum of values for that location)
def normalize_location_values():
  location_sums = {location_name:0 for location_name in location_names}

  # Find total sum of values for each location
  for organism_id in organism_ids:
    for location_name, value in location_data[organism_id].items():
      location_sums[location_name] += value

  # Normalize data table using total location sums
  for organism_id in organism_ids:
    location_data[organism_id] = {location_name:(value / location_sums[location_name]) for location_name, value in location_data[organism_id].items()}

# Ingest taxonomic hierarchies and build index of tax rank + name to all organisms within it
def read_taxonomic_hierarchy_file():
  with open('data/phyloseq_rootarch_taxa.tsv') as f:
    lines = f.readlines()
    table = [line.split() for line in lines]

    for row in table[1:]:
      organism_id = row[0]
      for i, name in enumerate(row[1:8]):
        rank = TAX_RANK_NAMES[i]
        if name in tax_ranks[rank]:
          tax_ranks[rank][name].add(organism_id)
        else:
          tax_ranks[rank][name] = set([organism_id])

read_raw_location_values_file()
normalize_location_values()
read_taxonomic_hierarchy_file()