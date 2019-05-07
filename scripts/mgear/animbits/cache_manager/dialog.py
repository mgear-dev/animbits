
# imports
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

# tool imports
from mgear.animbits.cache_manager.mayautils import kill_ui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from mgear.animbits.cache_manager.query import get_scene_rigs
from mgear.animbits.cache_manager.mayautils import install_script_job
from mgear.animbits.cache_manager.mayautils import kill_script_job
from mgear.animbits.cache_manager.query import get_model_group
from mgear.animbits.cache_manager.query import find_model_group_inside_rig
from mgear.animbits.cache_manager.query import get_timeline_values
from mgear.animbits.cache_manager.mayautils import generate_gpu_cache

# UI WIDGET NAME
UI_NAME = "mgear_cache_manager_qdialog"


class AnimbitsCacheManagerDialog(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    """ AnimbitsCacheManagerDialog mGear cache manager tool user interface

    AnimbitsCacheManagerDialog us the user interface for mGear's Animbits
    cache manager tool. The cache manager is a tool that allows artists to
    generate a GPU representation of the deformed mesh in a rig
    """

    def __init__(self, parent=None):
        super(AnimbitsCacheManagerDialog, self).__init__(parent)

        # checks for previous ui instances
        kill_ui("{}WorkspaceControl".format(UI_NAME))
        kill_ui(UI_NAME)

        # sets title and object name
        self.setWindowTitle("Animbits: Cache Manager")
        self.setObjectName(UI_NAME)

        # creates main layout widget
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setMargin(6)
        self.main_layout.setSpacing(6)

        # colors to use
        self.blue = QtGui.QColor(35, 140, 160)

        # creates ui widgets
        self._create_widgets()

        # fill ui content
        self._fill_widgets()

        # connects signals
        self._connect_signals()

        # adds refresh callback
        install_script_job(self.refresh_model)

    def _apply_filter(self):
        """ Uses the line edit text to filter the view
        """

        self.proxy_model.setFilterRegExp(self.filter_line.text())

    def _connect_signals(self):
        """ Connects widget signals to functionalities
        """

        self.filter_line.textChanged.connect(self._apply_filter)
        self.cache_button.clicked.connect(self.generate_cache)

    def _create_widgets(self):
        """ Creates the widget elements the user will interact with
        """

        # creates frame and add it to principal layout
        frame = QtWidgets.QFrame()
        frame.setFrameStyle(6)
        self.main_layout.addWidget(frame)

        # create layout for frame
        frame_layout = QtWidgets.QGridLayout(frame)
        frame_layout.setMargin(4)
        frame_layout.setSpacing(4)

        # creates search line edit
        filter_label = QtWidgets.QLabel("Search:")
        filter_help = "Type to filter your scene rigs"
        self.filter_line = QtWidgets.QLineEdit()
        self.filter_line.setObjectName("cache_manager_filter_qlineedit")
        self.filter_line.setToolTip(filter_help)
        self.filter_line.setWhatsThis(filter_help)
        self.filter_line.setPlaceholderText("Type to filter assets")

        # creates search list view
        self.rigs_list_view = QtWidgets.QListView()
        self.rigs_list_view.setAlternatingRowColors(True)
        self.rigs_list_view.setSelectionMode(
            self.rigs_list_view.ExtendedSelection)
        self.rigs_list_view.setEditTriggers(self.rigs_list_view.NoEditTriggers)

        # creates cache button
        self.cache_button = QtWidgets.QPushButton("Cache Selected")
        self.cache_button.setPalette(self.blue)

        # adds widgets to frame layout
        frame_layout.addWidget(filter_label, 0, 0, 1, 1)
        frame_layout.addWidget(self.filter_line, 1, 0, 1, 1)
        frame_layout.addWidget(self.rigs_list_view, 2, 0, 1, 1)
        frame_layout.addWidget(self.cache_button, 3, 0, 1, 1)

    def _fill_widgets(self):
        """ Fills the content on the widgets
        """

        # gets scene rigs
        data = get_scene_rigs()
        model = QtGui.QStringListModel(data)

        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(model)

        self.rigs_list_view.setModel(self.proxy_model)

    def dockCloseEventTriggered(self, *args, **kwargs):  # @unusedVariables
        """ Overwrites MayaQWidgetDockableMixin method
        """

        # kills installed script jobs
        kill_script_job(self.refresh_model.__name__)

    def generate_cache(self):
        """ Launches the GPU cache generation for the selected items
        """

        print("Generating caches...")

        start, end = get_timeline_values()

        items = self.rigs_list_view.selectedIndexes()
        model = self.rigs_list_view.model()

        for idx in items:
            name_idx = model.index(idx.row(), 0)
            rig_node = model.data(name_idx)
            geo_node = get_model_group()  # need to add selection here
            model_group = find_model_group_inside_rig(geo_node, rig_node)
            generate_gpu_cache(model_group, rig_node, start, end, rig_node)

    def refresh_model(self):
        """ Updates the rigs model list
        """

        data = get_scene_rigs()
        model = QtGui.QStringListModel(data)
        self.proxy_model.setSourceModel(model)
