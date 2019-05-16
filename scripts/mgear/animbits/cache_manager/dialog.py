
# imports
from __future__ import absolute_import
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# tool imports
from mgear.animbits.cache_manager.collapse_widget import QCollapse
from mgear.animbits.cache_manager.query import (
    get_scene_rigs,
    get_model_group,
    find_model_group_inside_rig,
    get_timeline_values,
    read_preference_key,
    get_cache_destination_path)

from mgear.animbits.cache_manager.mayautils import (
    kill_ui,
    install_script_job,
    kill_script_job,
    generate_gpu_cache,
    unload_rig,
    create_cache_manager_preference_file,
    set_preference_file_model_group,
    set_preference_file_unload_method,
    set_preference_file_cache_destination,
    load_rig)

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
        self.orange = QtGui.QColor(250, 180, 40)

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
        self.model_group_button.clicked.connect(self.set_model_group)
        self.path_group_button.clicked.connect(self.set_cache_path)
        self.rig_unload_radial.clicked.connect(self.set_unload_method)
        self.rig_hide_radial.clicked.connect(self.set_unload_method)
        self.cache_button.clicked.connect(self.generate_cache)
        self.rig_button.clicked.connect(self.reload_rig)

    def _create_widgets(self):
        """ Creates the widget elements the user will interact with
        """

        # options widgets -----------------------------------------------------
        options_widget = QCollapse(title="Options:")
        self.main_layout.addWidget(options_widget)

        frame_layout = QtWidgets.QGridLayout()
        frame_layout.setMargin(4)
        frame_layout.setSpacing(4)

        label = QtWidgets.QLabel("Options:")
        display_label = QtWidgets.QLabel("Rig switch:")
        self.rig_unload_radial = QtWidgets.QRadioButton("Unload")
        self.rig_unload_radial.setObjectName(
            "cache_manager_unload_qradialbutton")
        self.rig_unload_radial.setToolTip("Unload the rig after caching")
        self.rig_unload_radial.setChecked(True)
        self.rig_hide_radial = QtWidgets.QRadioButton("Hide")
        self.rig_hide_radial.setObjectName("cache_manager_hide_qradialbutton")
        self.rig_hide_radial.setToolTip("Hides the rig after caching")

        model_label = QtWidgets.QLabel("Model group:")
        filter_help = "Group name containing your shapes to cache"
        self.model_group_line = QtWidgets.QLineEdit()
        self.model_group_line.setObjectName("cache_manager_model_qlineedit")
        self.model_group_line.setToolTip(filter_help)
        self.model_group_line.setWhatsThis(filter_help)
        self.model_group_line.setPlaceholderText(
            "Group name containing your shapes")
        self.model_group_button = QtWidgets.QPushButton("Set")

        path_label = QtWidgets.QLabel("GPU path:")
        filter_help = "Path where GPU files will get stored"
        self.path_group_line = QtWidgets.QLineEdit()
        self.path_group_line.setObjectName("cache_manager_model_qlineedit")
        self.path_group_line.setToolTip(filter_help)
        self.path_group_line.setWhatsThis(filter_help)
        self.path_group_line.setPlaceholderText("Path where files get saved")
        self.path_group_line.setReadOnly(True)
        self.path_group_button = QtWidgets.QPushButton("...")

        # adds widgets to frame layout
        frame_layout.addWidget(label, 0, 0, 1, 1)
        frame_layout.addWidget(display_label, 1, 0, 1, 1)
        frame_layout.addWidget(self.rig_unload_radial, 1, 1, 1, 1)
        frame_layout.addWidget(self.rig_hide_radial, 1, 2, 1, 1)
        frame_layout.addWidget(model_label, 2, 0, 1, 1)
        frame_layout.addWidget(self.model_group_line, 2, 1, 1, 2)
        frame_layout.addWidget(self.model_group_button, 2, 3, 1, 1)
        frame_layout.addWidget(path_label, 3, 0, 1, 1)
        frame_layout.addWidget(self.path_group_line, 3, 1, 1, 2)
        frame_layout.addWidget(self.path_group_button, 3, 3, 1, 1)
        options_widget.set_layout(frame_layout)

        # search & filter widgets ---------------------------------------------
        frame = QtWidgets.QFrame()
        frame.setFrameStyle(6)
        self.main_layout.addWidget(frame)

        # create layout for frame
        frame_layout = QtWidgets.QGridLayout(frame)
        frame_layout.setMargin(4)
        frame_layout.setSpacing(4)

        # creates search line edit
        label = QtWidgets.QLabel("Search:")
        filter_help = "Type to filter your scene rigs"
        self.filter_line = QtWidgets.QLineEdit()
        self.filter_line.setObjectName("cache_manager_filter_qlineedit")
        self.filter_line.setToolTip(filter_help)
        self.filter_line.setWhatsThis(filter_help)
        self.filter_line.setPlaceholderText("Type to filter assets")

        # creates search list view
        self.rigs_list_view = QtWidgets.QListView()
        self.rigs_list_view.setObjectName("cache_manager_rigs_qlistview")
        self.rigs_list_view.setAlternatingRowColors(True)
        self.rigs_list_view.setSelectionMode(
            self.rigs_list_view.ExtendedSelection)
        self.rigs_list_view.setEditTriggers(self.rigs_list_view.NoEditTriggers)

        # adds widgets to frame layout
        frame_layout.addWidget(label, 0, 0, 1, 1)
        frame_layout.addWidget(self.filter_line, 1, 0, 1, 1)
        frame_layout.addWidget(self.rigs_list_view, 2, 0, 1, 1)

        # buttons widgets -----------------------------------------------------
        frame = QtWidgets.QFrame()
        frame.setFrameStyle(6)
        self.main_layout.addWidget(frame)

        # create layout for frame
        frame_layout = QtWidgets.QGridLayout(frame)
        frame_layout.setMargin(4)
        frame_layout.setSpacing(4)

        # creates cache button
        self.cache_button = QtWidgets.QPushButton("Cache Selected")
        self.cache_button.setObjectName("cache_manager_cache_qpushbutton")
        self.cache_button.setPalette(self.blue)

        # creates rig button
        self.rig_button = QtWidgets.QPushButton("Set Rig")
        self.rig_button.setObjectName("cache_manager_rig_qpushbutton")
        self.rig_button.setPalette(self.orange)

        # adds widgets to frame layout
        frame_layout.addWidget(self.cache_button, 1, 0, 1, 1)
        frame_layout.addWidget(self.rig_button, 2, 0, 1, 1)

    def _fill_widgets(self):
        """ Fills the content on the widgets
        """

        # sets unload method
        if read_preference_key("cache_manager_unload_rigs") == 1:
            self.rig_unload_radial.setChecked(True)
        elif read_preference_key("cache_manager_unload_rigs") == 0:
            self.rig_hide_radial.setChecked(True)

        # fills model group name preference
        geo_node = get_model_group(True)
        if geo_node:
            self.model_group_line.setText(geo_node)

        # fills gpu cache destination path
        self.path_group_line.setText(get_cache_destination_path())

        # fills with scene rigs
        data = get_scene_rigs()
        model = QtGui.QStringListModel(data)

        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(model)

        self.rigs_list_view.setModel(self.proxy_model)

        timer = QtCore.QTimer(self)
        timer.singleShot(0, self.filter_line.setFocus)

    def _show_browser(self):
        """
        """

        brower = QtWidgets.QFileDialog(self)
        brower.setFileMode(brower.DirectoryOnly)
        return brower.getExistingDirectory()

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

        for idx in items:
            rig_node = idx.data()
            geo_node = get_model_group()  # need to add selection here
            model_group = find_model_group_inside_rig(geo_node, rig_node)
            gpu_node = generate_gpu_cache(model_group, rig_node, start, end,
                                          rig_node, True)
            if gpu_node:
                unload_rig(rig_node, self.rig_unload_radial.isChecked())

    def refresh_model(self):
        """ Updates the rigs model list
        """

        data = get_scene_rigs()
        model = QtGui.QStringListModel(data)
        self.proxy_model.setSourceModel(model)

    def reload_rig(self):
        """ Reloads rigs for the selected items
        """

        print("Reloading rigs...")

        items = self.rigs_list_view.selectedIndexes()

        for idx in items:
            rig_node = idx.data()
            load_rig(rig_node)

    def set_cache_path(self):
        """ Sets the cache path inside the preference file
        """

        create_cache_manager_preference_file()
        _path = self._show_browser()
        if _path:
            self.path_group_line.setText(_path)
            set_preference_file_cache_destination(_path)

    def set_model_group(self):
        """ Saves he model group name into the preference file
        """

        create_cache_manager_preference_file()
        set_preference_file_model_group(self.model_group_line.text())

    def set_unload_method(self):
        """ Saves the unloading method into the preference file
        """

        create_cache_manager_preference_file()
        if self.rig_unload_radial.isChecked():
            set_preference_file_unload_method(1)
        else:
            set_preference_file_unload_method(0)


def run_cache_mamanger(*args):  # @unusedVariable
    """ Opens the Cache Manager UI
    """

    tool = AnimbitsCacheManagerDialog()
    tool.show(dockable=True)
