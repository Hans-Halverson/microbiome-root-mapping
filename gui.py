from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QCheckBox, QColorDialog, QComboBox, QCompleter, QErrorMessage, QFileDialog, QFrame, QLineEdit, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from os import path
import sys

from strains import ASV_KEY
from taxa import TAXA
from visualize import IMAGE_HEIGHT, IMAGE_WIDTH, render_image

APP_NAME = "Microbiome Root Mapping"
ICON_PATH = path.join(path.dirname(__file__), "resources", "icon.png")

ASV_SELECTOR_INDEX = len(TAXA)

BUTTON_WIDTH = 80
NAME_INPUT_WIDTH = 250
TAXA_SELECTOR_WIDTH = 100

IMAGE_PREVIEW_WIDTH = 1200
IMAGE_PREVIEW_HEIGHT = 675

WINDOW_WIDTH = IMAGE_PREVIEW_WIDTH + 40
WINDOW_HEIGHT = IMAGE_PREVIEW_HEIGHT + 110

class Window(QWidget):
  def __init__(self, app, indexed_strains):
    super().__init__()

    self.app = app
    self.indexed_strains = indexed_strains
    self.current_viewed_strains = None
    self.current_viewed_name = "image"
    self.current_color = (255, 0, 0)
    self.hide_name = False
 
    self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
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
    vbox.addWidget(preview, 1)

    self.setLayout(vbox)
    self.show()

  def init_name_input_completers(self):
    self.name_input_completers = dict()
    for taxon, names in self.indexed_strains.items():
      if taxon == ASV_KEY:
        sorted_names = sorted(names, key=lambda name: int(name[4:]))
      else:
        sorted_names = sorted(names)
      completer = QCompleter(sorted_names)
      completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
      completer.setMaxVisibleItems(20)
      self.name_input_completers[taxon] = completer
  
  def build_toolbar(self):
    # Create name input components
    self.taxa_selector = QComboBox()
    self.name_input = QLineEdit()
    self.view_button = QPushButton("View")

    self.taxa_selector.addItems([taxon.value for taxon in TAXA] + [ASV_KEY])
    self.taxa_selector.setFixedWidth(TAXA_SELECTOR_WIDTH)
    self.taxa_selector.currentIndexChanged.connect(self.on_change_selected_taxa)
    self.on_change_selected_taxa(0)

    self.name_input.textChanged.connect(self.on_name_text_changed)
    self.name_input.setFixedWidth(NAME_INPUT_WIDTH)
    self.on_name_text_changed("")

    self.view_button.setFixedWidth(BUTTON_WIDTH)
    self.view_button.clicked.connect(self.on_view_button_clicked)

    # Create visualize input components
    self.choose_color_button = QPushButton("Choose Color")
    self.choose_color_button.setFixedWidth(BUTTON_WIDTH * 1.65)
    self.choose_color_button.setToolTip("Choose color for image")
    self.choose_color_button.clicked.connect(self.on_choose_color_button_clicked)
    self.update_choose_color_preview()

    hide_name_checkbox = QCheckBox("Hide Name")
    hide_name_checkbox.setToolTip("Do not show name on image")
    hide_name_checkbox.toggled.connect(self.on_hide_name_checkbox_toggled)

    # Create right buttons
    self.save_button = QPushButton("Save Image")
    self.save_button.setFixedWidth(BUTTON_WIDTH * 1.5)
    self.save_button.clicked.connect(self.on_save_button_clicked)

    quit_button = QPushButton("Quit")
    quit_button.setFixedWidth(BUTTON_WIDTH)
    quit_button.clicked.connect(self.on_quit_button_clicked)

    # Group name inputs on left
    name_inputs_hbox = QHBoxLayout()
    name_inputs_hbox.addWidget(self.taxa_selector)
    name_inputs_hbox.addWidget(self.name_input)
    name_inputs_hbox.addWidget(self.view_button)

    # Group visualize inputs in middle
    visualize_inputs_hbox = QHBoxLayout()
    visualize_inputs_hbox.addWidget(self.choose_color_button)
    visualize_inputs_hbox.addWidget(hide_name_checkbox)

    # Group buttons on right
    right_buttons_hbox = QHBoxLayout()
    right_buttons_hbox.addWidget(self.save_button)
    right_buttons_hbox.addWidget(quit_button)

    # Add inputs and right buttons to toolbar component
    toolbar_hbox = QHBoxLayout()
    toolbar_hbox.addLayout(name_inputs_hbox)
    toolbar_hbox.addStretch()
    toolbar_hbox.addLayout(visualize_inputs_hbox)
    toolbar_hbox.addStretch()
    toolbar_hbox.addLayout(right_buttons_hbox)
    toolbar_hbox.setAlignment(Qt.AlignLeft)

    return toolbar_hbox

  def build_init_preview(self):
    self.preview = QLabel()
    self.preview.setScaledContents(True)
    self.preview.setFixedSize(IMAGE_PREVIEW_WIDTH, IMAGE_PREVIEW_HEIGHT)
    self.render_preview([], [])

    return self.preview

  def on_change_selected_taxa(self, i):
    taxon = TAXA[i] if i < ASV_SELECTOR_INDEX else ASV_KEY
    self.current_taxon = taxon
    self.name_input.clear()
    self.name_input.setCompleter(self.name_input_completers[taxon])
  
  def on_name_text_changed(self, name):
    self.current_name = name
    is_valid = name in self.indexed_strains[self.current_taxon]
    if is_valid:
      self.view_button.setEnabled(True)
      self.view_button.setToolTip("")
    else:
      self.view_button.setEnabled(False)
      tooltip = "Input name of strain" if name == "" else f"No strains found with name \"{name}\""
      self.view_button.setToolTip(tooltip)
  
  def on_view_button_clicked(self):
    strains = self.indexed_strains[self.current_taxon][self.current_name]
    self.current_viewed_strains = strains
    self.current_viewed_name = self.current_name

    # Find full taxonomic hierarchy
    strain = strains[0]
    if self.current_taxon == ASV_KEY:
      first_missing_taxon = next(filter(lambda taxon: strain.get_taxon_name(taxon) is None, TAXA), None)
      current_taxon_index = len(TAXA) - 1 if first_missing_taxon is None else TAXA.index(first_missing_taxon) - 1
    else:
      current_taxon_index = TAXA.index(self.current_taxon)
    hierarchy = [strain.get_taxon_name(TAXA[i]) for i in range(current_taxon_index + 1)]

    self.render_preview(strains, hierarchy)
    
  def render_preview(self, strains, hierarchy):
    self.current_image = render_image(strains, [] if self.hide_name else hierarchy, self.current_color)
    image_bytes = self.current_image.tobytes("raw", "BGRA")
    qt_image = QtGui.QImage(image_bytes, IMAGE_WIDTH, IMAGE_HEIGHT, QtGui.QImage.Format_ARGB32)
    pixmap = QtGui.QPixmap.fromImage(qt_image)
    self.preview.setPixmap(pixmap)

  def on_choose_color_button_clicked(self):
    initial_color = QtGui.QColor(self.current_color[0], self.current_color[1], self.current_color[2])
    color = QColorDialog.getColor(initial_color)
    if color.isValid():
      self.current_color = (color.red(), color.green(), color.blue())
      self.update_choose_color_preview()

  def update_choose_color_preview(self):
    color_pixmap = QtGui.QPixmap(10, 10)
    color_pixmap.fill(QtGui.QColor(self.current_color[0], self.current_color[1], self.current_color[2]))
    self.choose_color_button.setIcon(QtGui.QIcon(color_pixmap))
  
  def on_hide_name_checkbox_toggled(self, hide_name):
    self.hide_name = hide_name

  def on_save_button_clicked(self):
    file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", self.current_viewed_name + ".png", "Images (*.png)")
    if file_name != "":
      try:
        self.current_image.save(file_name)
      except:
        error = QErrorMessage(self)
        error.showMessage("Could not save file")
        error.setWindowModality(Qt.WindowModal)
  
  def on_quit_button_clicked(self):
    self.app.exit()

def init(indexed_strains):
  app = QApplication([])
  app.setApplicationName(APP_NAME)
  app.setWindowIcon(QtGui.QIcon(ICON_PATH))

  window = Window(app, indexed_strains)

  sys.exit(app.exec_())