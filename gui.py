from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QComboBox, QCompleter, QFileDialog, QFrame, QLineEdit, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

import sys

from taxa import TAXA, Taxon

APP_NAME = "Microbiome Root Mapping"
ICON_PATH = "icon.png"

BUTTON_WIDTH = 80
NAME_INPUT_WIDTH = 250
TAXA_SELECTOR_WIDTH = 100

class Window(QWidget):
  def __init__(self, app, strains):
    super().__init__()

    self.app = app
    self.strains = strains
    self.current_viewed_strains = None
    self.current_viewed_name = ""
 
    self.setGeometry(0, 0, 1200, 800)
    self.setWindowTitle(APP_NAME)
    self.setWindowIcon(QtGui.QIcon(ICON_PATH))

    self.init_name_input_completers()
    toolbar = self.build_toolbar()
    preview = self.build_init_preview()

    vbox_divider = QFrame()
    vbox_divider.setFrameShape(QFrame.Shape.HLine)
    vbox_divider.setFrameShadow(QFrame.Shadow.Sunken)

    vbox = QVBoxLayout()
    vbox.addLayout(toolbar)
    vbox.addWidget(vbox_divider)
    vbox.addLayout(preview, 1)

    self.setLayout(vbox)
    self.show()

  def init_name_input_completers(self):
    self.name_input_completers = dict()
    for taxon, names in self.strains.items():
      completer = QCompleter(names)
      completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
      self.name_input_completers[taxon] = completer
  
  def build_toolbar(self):
    # Create input components
    self.taxa_selector = QComboBox()
    self.name_input = QLineEdit()
    self.view_button = QPushButton("View")

    self.taxa_selector.addItems([taxon.value for taxon in TAXA])
    self.taxa_selector.setFixedWidth(TAXA_SELECTOR_WIDTH)
    self.taxa_selector.currentIndexChanged.connect(self.on_change_selected_taxa)
    self.on_change_selected_taxa(0)

    self.name_input.textChanged.connect(self.on_name_text_changed)
    self.name_input.setFixedWidth(NAME_INPUT_WIDTH)
    self.on_name_text_changed("")

    self.view_button.setFixedWidth(BUTTON_WIDTH)
    self.view_button.clicked.connect(self.on_view_button_clicked)

    # Create right buttons
    self.save_button = QPushButton("Save")
    self.save_button.setEnabled(False)
    self.save_button.setToolTip("No image to save")
    self.save_button.setFixedWidth(BUTTON_WIDTH)
    self.save_button.clicked.connect(self.on_save_button_clicked)

    quit_button = QPushButton("Quit")
    quit_button.setFixedWidth(BUTTON_WIDTH)
    quit_button.clicked.connect(self.on_quit_button_clicked)

    # Group inputs on left
    left_bar_inputs_hbox = QHBoxLayout()
    left_bar_inputs_hbox.addWidget(self.taxa_selector)
    left_bar_inputs_hbox.addWidget(self.name_input)
    left_bar_inputs_hbox.addWidget(self.view_button)

    # Group buttons on right
    right_buttons_hbox = QHBoxLayout()
    right_buttons_hbox.addWidget(self.save_button)
    right_buttons_hbox.addWidget(quit_button)

    # Add inputs and right buttons to toolbar component
    toolbar_hbox = QHBoxLayout()
    toolbar_hbox.addLayout(left_bar_inputs_hbox)
    toolbar_hbox.addStretch()
    toolbar_hbox.addLayout(right_buttons_hbox)
    toolbar_hbox.setAlignment(Qt.AlignLeft)

    return toolbar_hbox

  def build_init_preview(self):
    self.preview_text = QLabel()
    self.preview_text.setText("Select strains to visualize")

    self.preview = QVBoxLayout()
    self.preview.addWidget(self.preview_text, 0, Qt.AlignHCenter)

    return self.preview

  def on_change_selected_taxa(self, i):
    taxon = TAXA[i]
    self.current_taxon = taxon
    self.name_input.clear()
    self.name_input.setCompleter(self.name_input_completers[taxon])
  
  def on_name_text_changed(self, name):
    self.current_name = name
    is_valid = name in self.strains[self.current_taxon]
    if is_valid:
      self.view_button.setEnabled(True)
      self.view_button.setToolTip("")
    else:
      self.view_button.setEnabled(False)
      tooltip = "Input name of strain" if name == "" else f"No strains found with name \"{name}\""
      self.view_button.setToolTip(tooltip)
  
  def on_view_button_clicked(self):
    if self.current_viewed_strains is None:
      self.save_button.setEnabled(True)
      self.save_button.setToolTip("")

    strains = self.strains[self.current_taxon][self.current_name]
    self.current_viewed_strains = strains
    self.current_viewed_name = self.current_name

    # Find full taxonomic hierarchy
    strain = strains[0]
    current_taxon_index = TAXA.index(self.current_taxon)
    hierarchy = [strain.get_taxa_name(TAXA[i]) for i in range(current_taxon_index + 1)]

    self.preview_text.setText("  >  ".join(hierarchy))
  
  def on_save_button_clicked(self):
    file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", self.current_viewed_name + ".png")
    if file_name != "":
      print(f"<Saved {file_name}>")
  
  def on_quit_button_clicked(self):
    self.app.exit()

def init(strains):
  app = QApplication([])
  app.setApplicationName(APP_NAME)
  app.setWindowIcon(QtGui.QIcon(ICON_PATH))

  window = Window(app, strains)

  sys.exit(app.exec_())