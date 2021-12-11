import gui
import strains

if __name__ == "__main__":
  all_strains = strains.parse_strains_files()
  strains_indices = strains.build_strains_indices(all_strains)
  gui.init(all_strains, strains_indices)
