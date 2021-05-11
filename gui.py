from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QComboBox, QCompleter, QFormLayout, QFrame, QLayout, QLineEdit, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

import sys

from taxa import ORDERED_TAXA, Taxa

class Window(QWidget):
  def __init__(self, strains):
    super().__init__()

    self.strains = strains
 
    self.setGeometry(0, 0, 1200, 800)
    self.setWindowTitle('Microbiome Root Mapping')

    hbox = QHBoxLayout()
    left_bar_vbox = QVBoxLayout()
    left_bar_inputs = QFormLayout()

    taxa_selector = QComboBox()
    self.name_input = QLineEdit()
    self.submit_button = QPushButton("Submit")

    self.init_name_input_completers()

    taxa_selector.addItems([taxa.value for taxa in ORDERED_TAXA])
    taxa_selector.currentIndexChanged.connect(self.on_change_selected_taxa)
    self.on_change_selected_taxa(0)

    self.name_input.textChanged.connect(self.on_name_text_changed)
    self.on_name_text_changed("")

    self.submit_button.clicked.connect(self.on_submit_button_clicked)
 
    preview = QLabel()
    preview.setText("<Preview goes here>")

    hbox_divider = QFrame()
    hbox_divider.setFrameShape(QFrame.Shape.VLine)
    hbox_divider.setFrameShadow(QFrame.Shadow.Sunken)

    left_bar_inputs.addRow("Rank:", taxa_selector)
    left_bar_inputs.addRow("Name:", self.name_input)

    left_bar_vbox.addLayout(left_bar_inputs)
    left_bar_vbox.addWidget(self.submit_button)
  
    hbox.addLayout(left_bar_vbox)
    hbox.addWidget(hbox_divider)
    hbox.addWidget(preview, 1)
    self.setLayout(hbox)

    self.show()

  def init_name_input_completers(self):
    self.name_input_completers = dict()
    for taxa, names in self.strains.items():
      completer = QCompleter(names)
      completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
      self.name_input_completers[taxa] = completer
  
  def on_change_selected_taxa(self, i):
    taxa = ORDERED_TAXA[i]
    self.selected_taxa = taxa
    self.name_input.clear()
    self.name_input.setCompleter(self.name_input_completers[taxa])
  
  def on_name_text_changed(self, name):
    self.current_name = name
    is_valid = name in self.strains[self.selected_taxa]
    if is_valid:
      self.submit_button.setEnabled(True)
      self.submit_button.setToolTip("")
    else:
      self.submit_button.setEnabled(False)
      tooltip = "Input name of strain" if name == "" else f"No strains found with name \"{name}\""
      self.submit_button.setToolTip(tooltip)
  
  def on_submit_button_clicked(self):
    print("<Visualize>")

def init(strains):
  app = QApplication([])
  window = Window(strains)
  sys.exit(app.exec_())