
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
        kill_ui(UI_NAME)
        kill_ui("{}WorkspaceControl".format(UI_NAME))

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

    def refresh_model(self):
        """ Updates the rigs model list
        """

        data = get_scene_rigs()
        model = QtGui.QStringListModel(data)
        self.proxy_model.setSourceModel(model)
