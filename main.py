import gui
import strains

if __name__ == "__main__":
  all_strains = strains.parse_strains_file()
  strains_index = strains.build_strains_index(all_strains)
  gui.init(all_strains, strains_index)
