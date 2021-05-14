from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QCheckBox, QColorDialog, QComboBox, QCompleter, QErrorMessage, QFileDialog, QFrame, QLineEdit, QLabel, QHBoxLayout, QPushButton, QSlider, QVBoxLayout, QWidget
from PyQt5.QtCore import QSize, QTimer, Qt

from os import path
import sys

from strains import ASV_KEY
from taxa import TAXA, Taxon
from visualize import IMAGE_HEIGHT, IMAGE_WIDTH, render_image

APP_NAME = "Microbiome Root Mapping"
ICON_PATH = path.join(path.dirname(__file__), "resources", "icon.png")

ASV_SELECTOR_INDEX = len(TAXA)

BUTTON_WIDTH = 80
NAME_INPUT_WIDTH = 250
TAXA_SELECTOR_WIDTH = 100

IMAGE_PREVIEW_WIDTH = 1200
IMAGE_PREVIEW_HEIGHT = 675

WINDOW_WIDTH_PADDING = 40
WINDOW_HEIGHT_PADDING = 110

WINDOW_WIDTH = IMAGE_PREVIEW_WIDTH + WINDOW_WIDTH_PADDING
WINDOW_HEIGHT = IMAGE_PREVIEW_HEIGHT + WINDOW_HEIGHT_PADDING

RENDER_DEBOUNCE_TIMEOUT = 200

class Window(QWidget):
  def __init__(self, app, all_strains, indexed_strains):
    super().__init__()

    self.app = app
    self.all_strains = all_strains
    self.indexed_strains = indexed_strains
    self.current_name = ""
    self.current_taxon = TAXA[0]
    self.current_scale = 1000
    self.current_color = (255, 0, 0)
    self.hide_name = False

    # Set up debounced rendering
    self.render_debounce = QTimer()
    self.render_debounce.setInterval(RENDER_DEBOUNCE_TIMEOUT)
    self.render_debounce.setSingleShot(True)
    self.render_debounce.timeout.connect(self.render_preview)
 
    self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
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
    # Determine which strains should be displayed
    strains_to_display = set()
    taxa_to_display = {taxon:set() for taxon in TAXA}
    taxa_to_display[ASV_KEY] = set()
    for strain in self.all_strains:
      if sum(strain.values) > 0.0055:
        strains_to_display.add(strain)
        for taxon in TAXA:
          name = strain.get_taxon_name(taxon)
          if name is not None:
            taxa_to_display[taxon].add(strain.get_taxon_name(taxon))
        taxa_to_display[ASV_KEY].add(strain.id)

    self.name_input_completers = dict()
    for taxon, names in taxa_to_display.items():      
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

    self.taxa_selector.addItems([taxon.value for taxon in TAXA] + [ASV_KEY])
    self.taxa_selector.setFixedWidth(TAXA_SELECTOR_WIDTH)
    self.taxa_selector.currentIndexChanged.connect(self.on_change_selected_taxa)

    self.name_input.textChanged.connect(self.on_name_text_changed)
    self.name_input.setFixedWidth(NAME_INPUT_WIDTH)
    self.name_input.setCompleter(self.name_input_completers[self.current_taxon])
    self.name_input.setToolTip("Search for phlyum to display")
    self.on_name_text_changed("")

    # Create visualize input components
    scale_tooltip = "Scale for colors on image"
    scale_label = QLabel("Scale:")
    scale_label.setToolTip(scale_tooltip)

    self.scale_text_input = QLineEdit()
    self.scale_text_input.setText(str(self.current_scale))
    self.scale_text_input.setFixedWidth(40)
    self.scale_text_input.textEdited.connect(self.on_scale_text_input_edited)
    self.scale_text_input.setToolTip(scale_tooltip)

    self.scale_slider = QSlider(Qt.Horizontal)
    self.scale_slider.setMinimum(1)
    self.scale_slider.setMaximum(5000)
    self.scale_slider.setValue(self.current_scale)
    self.scale_slider.valueChanged.connect(self.on_scale_slider_change)
    self.scale_slider.setToolTip(scale_tooltip)

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

    # Group visualize inputs in middle
    visualize_inputs_hbox = QHBoxLayout()
    visualize_inputs_hbox.addWidget(scale_label)
    visualize_inputs_hbox.addWidget(self.scale_text_input)
    visualize_inputs_hbox.addWidget(self.scale_slider)
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
    self.preview.setMinimumSize(1, 1)
    self.render_preview()

    return self.preview

  def on_change_selected_taxa(self, i):
    taxon = TAXA[i] if i < ASV_SELECTOR_INDEX else ASV_KEY
    self.current_taxon = taxon
    self.name_input.clear()
    self.name_input.setCompleter(self.name_input_completers[taxon])
    self.name_input.setToolTip(f"Search for {'ASV' if taxon == ASV_KEY else taxon.value.lower()} to display")
    self.render_preview()
  
  def on_name_text_changed(self, name):
    self.current_name = name
    is_valid = name in self.indexed_strains[self.current_taxon]
    if is_valid:
      self.render_preview()

  def render_preview(self):
    if self.current_name not in self.indexed_strains[self.current_taxon]:
      strains = []
      hierarchy = []
    else:
      strains = self.indexed_strains[self.current_taxon][self.current_name]
      # Find full taxonomic hierarchy
      strain = strains[0]
      if self.current_taxon == ASV_KEY:
        first_missing_taxon = next(filter(lambda taxon: strain.get_taxon_name(taxon) is None, TAXA), None)
        current_taxon_index = len(TAXA) - 1 if first_missing_taxon is None else TAXA.index(first_missing_taxon) - 1
      else:
        current_taxon_index = TAXA.index(self.current_taxon)
      hierarchy = [strain.get_taxon_name(TAXA[i]) for i in range(current_taxon_index + 1)]

    self.current_image = render_image(strains, [] if self.hide_name else hierarchy, self.current_color, self.current_scale)
    image_bytes = self.current_image.tobytes("raw", "BGRA")
    self.qt_image = QtGui.QImage(image_bytes, IMAGE_WIDTH, IMAGE_HEIGHT, QtGui.QImage.Format_ARGB32)
    self.resize_preview_image()
  
  def on_scale_slider_change(self, scale):
    self.current_scale = scale
    self.scale_text_input.setText(str(scale))
    self.render_debounce.start()

  def on_scale_text_input_edited(self, value):
    try:
      value = int(value)
    except:
      value = 1
    
    self.scale_slider.setValue(int(value))

  def on_choose_color_button_clicked(self):
    initial_color = QtGui.QColor(self.current_color[0], self.current_color[1], self.current_color[2])
    color = QColorDialog.getColor(initial_color)
    if color.isValid():
      self.current_color = (color.red(), color.green(), color.blue())
      self.update_choose_color_preview()
      self.render_preview()

  def update_choose_color_preview(self):
    color_pixmap = QtGui.QPixmap(10, 10)
    color_pixmap.fill(QtGui.QColor(self.current_color[0], self.current_color[1], self.current_color[2]))
    self.choose_color_button.setIcon(QtGui.QIcon(color_pixmap))
  
  def on_hide_name_checkbox_toggled(self, hide_name):
    self.hide_name = hide_name
    self.render_preview()

  def on_save_button_clicked(self):
    file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", self.current_name + ".png", "Images (*.png)")
    if file_name != "":
      try:
        self.current_image.save(file_name)
      except:
        error = QErrorMessage(self)
        error.showMessage("Could not save file")
        error.setWindowModality(Qt.WindowModal)
  
  def on_quit_button_clicked(self):
    self.app.exit()

  def resize_preview_image(self):
    width = self.width() - WINDOW_WIDTH_PADDING
    height = (float(IMAGE_PREVIEW_HEIGHT) / float(IMAGE_PREVIEW_WIDTH)) * width
    pixmap = QtGui.QPixmap.fromImage(self.qt_image.smoothScaled(width, height))
    self.preview.setPixmap(pixmap)

  def resizeEvent(self, _event):
    self.resize_preview_image()

def init(all_strains, indexed_strains):
  app = QApplication([])
  app.setApplicationName(APP_NAME)
  app.setWindowIcon(QtGui.QIcon(ICON_PATH))

  window = Window(app, all_strains, indexed_strains)

  sys.exit(app.exec_())