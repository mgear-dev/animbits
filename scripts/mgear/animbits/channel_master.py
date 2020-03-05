import maya.cmds as cmds
import pymel.core as pm
from mgear.core import pyflow_widgets
from mgear.core import pyqt
from mgear.vendor.Qt import QtWidgets
from mgear.vendor.Qt import QtCore
from mgear.vendor.Qt import QtGui
import timeit
from functools import partial
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin



from . import channel_master_utils as cmu
from . import channel_master_widgets as cmw

class ChannelMaster(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, attrs, parent=None):
        super(ChannelMaster, self).__init__(parent)
        self.deleteLater = True
        self.attrs = attrs

        self.setWindowTitle("Channel Master")
        self.setMinimumWidth(155)
        if cmds.about(ntOS=True):
            flags = self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
            self.setWindowFlags(flags)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, 1)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.refresh_channels()

    def create_actions(self):
        # file actions
        self.file_export_all_action = QtWidgets.QAction("Export All Tabs",
                                                        self)
        self.file_export_all_action.setIcon(pyqt.get_icon("log-out"))
        self.file_export_current_action = QtWidgets.QAction(
            "Export Current Tab", self)
        self.file_export_current_action.setIcon(pyqt.get_icon("log-out"))
        self.file_import_action = QtWidgets.QAction("Import", self)
        self.file_import_action.setIcon(pyqt.get_icon("log-in"))

        # Display actions
        self.display_fullname_action = QtWidgets.QAction(
            "Channel Full Name", self)
        self.display_fullname_action.setCheckable(True)
        self.display_fullname_action.setShortcut(QtGui.QKeySequence("Ctrl+F"))
        self.display_order_default_action = QtWidgets.QAction(
            "Default", self)
        self.display_order_alphabetical_action = QtWidgets.QAction(
            "Alphabetical", self)

        # Key actions
        self.key_all_action = QtWidgets.QAction("Keyframe", self)
        self.key_all_action.setIcon(pyqt.get_icon("key"))
        self.key_all_action.setShortcut(QtGui.QKeySequence("S"))
        self.key_copy_action = QtWidgets.QAction("Copy Key", self)
        self.key_copy_action.setIcon(pyqt.get_icon("copy"))
        self.key_copy_action.setShortcut(QtGui.QKeySequence("Ctrl+C"))
        self.key_paste_action = QtWidgets.QAction("Paste Key", self)
        self.key_paste_action.setIcon(pyqt.get_icon("clipboard"))
        self.key_paste_action.setShortcut(QtGui.QKeySequence("Ctrl+V"))
        self.key_all_tabs_action = QtWidgets.QAction(
            "Keyframe All Tabs", self)
        self.key_all_tabs_action.setCheckable(True)

        self.key_del_frame_action = QtWidgets.QAction(
            "Delete Current Frame Keyframe", self)
        self.key_del_frame_action.setIcon(pyqt.get_icon("trash-2"))
        self.key_del_frame_action.setShortcut(QtGui.QKeySequence("Shift+S"))

        # Tabs Actions
        self.tab_new_action = QtWidgets.QAction("New Tab", self)
        self.tab_new_action.setIcon(pyqt.get_icon("menu"))
        self.tab_del_action = QtWidgets.QAction("Delete Current Tab", self)
        self.tab_del_action.setIcon(pyqt.get_icon("trash-2"))
        self.tab_dup_action = QtWidgets.QAction("Duplicate Tab", self)
        self.tab_dup_action.setIcon(pyqt.get_icon("copy"))

    def create_widgets(self):
        # Menu bar
        self.menu_bar = QtWidgets.QMenuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(self.file_export_all_action)
        self.file_menu.addAction(self.file_export_current_action)
        self.file_menu.addAction(self.file_import_action)

        self.display_menu = self.menu_bar.addMenu("Display")
        self.display_menu.addAction(self.display_fullname_action)
        self.display_menu.addSeparator()
        self.order_menu = self.display_menu.addMenu("Order")
        self.order_menu.addAction(self.display_order_default_action)
        self.order_menu.addAction(self.display_order_alphabetical_action)

        self.key_menu = self.menu_bar.addMenu("Keyframe")
        self.key_menu.addAction(self.key_all_action)
        self.key_menu.addSeparator()
        self.key_menu.addAction(self.key_copy_action)
        self.key_menu.addAction(self.key_paste_action)
        self.key_menu.addSeparator()
        self.key_menu.addAction(self.key_del_frame_action)
        self.key_menu.addSeparator()
        self.key_menu.addAction(self.key_all_tabs_action)

        self.tab_menu = self.menu_bar.addMenu("Tab")
        self.tab_menu.addAction(self.tab_new_action)
        self.tab_menu.addAction(self.tab_dup_action)
        self.tab_menu.addSeparator()
        self.tab_menu.addAction(self.tab_del_action)

        # Keyframe widgets
        self.key_all_button = cmw.create_button(
            size=34, icon="key", toolTip="Keyframe")
        self.key_copy_button = cmw.create_button(
            size=34, icon="copy", toolTip="Copy Keyframe")
        self.key_paste_button = cmw.create_button(
            size=34, icon="clipboard", toolTip="Paste Keyframe")

        # channel listing widgets
        self.lock_button = cmw.create_button(
            size=34,
            icon="unlock",
            toggle_icon="lock",
            toolTip="Lock Channel Auto Refresh")
        self.refresh_button = cmw.create_button(
            size=34, icon="refresh-cw", toolTip="Refresh Channel List")
        self.add_channel_button = cmw.create_button(
            size=17, icon="plus", toolTip="Add Selected Channels")
        self.remove_channel_button = cmw.create_button(
            size=17, icon="minus", toolTip="Remove Selected Channels")

        # search widgets
        self.search_label = QtWidgets.QLabel("Filter Channel: ")
        self.search_lineEdit = QtWidgets.QLineEdit()
        self.search_clear_button = cmw.create_button(
            size=17, icon="delete", toolTip="Clear Search Field")

        # tabs widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.add_tab_button = cmw.create_button(
            size=17, icon="plus", toolTip="Add New Tab")
        self.add_tab_button.setFlat(True)
        self.add_tab_button.setMaximumWidth(34)

        self.tab_widget.setCornerWidget(self.add_tab_button,
                                        corner=QtCore.Qt.TopRightCorner)

        # Channels table
        pass

    def create_layout(self):

        table_style = """
        QTableView {
           border: 0 solid transparent;
        }
        """

       # border-radius: 5px;
       # height: 32px;
        line_edit_style = """
        QLineEdit {
           border: 0 solid transparent;
           margin-right: 2px;
           margin-left: 2px;
        }
        """

        # main Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)
        main_layout.setMenuBar(self.menu_bar)

        # keyframe buttons Layout
        # key_copypaste_buttons_layout = QtWidgets.QVBoxLayout()
        # key_copypaste_buttons_layout.addWidget(self.key_copy_button)
        # key_copypaste_buttons_layout.addWidget(self.key_paste_button)
        key_buttons_layout = QtWidgets.QHBoxLayout()
        key_buttons_layout.addWidget(self.key_all_button)
        key_buttons_layout.addWidget(self.key_copy_button)
        key_buttons_layout.addWidget(self.key_paste_button)
        # key_buttons_layout.addLayout(key_copypaste_buttons_layout)

        # channel listing buttons Layout
        channel_add_remove_buttons_layout = QtWidgets.QVBoxLayout()
        channel_add_remove_buttons_layout.addWidget(self.add_channel_button)
        channel_add_remove_buttons_layout.addWidget(self.remove_channel_button)
        channel_buttons_layout = QtWidgets.QHBoxLayout()
        channel_buttons_layout.addLayout(channel_add_remove_buttons_layout)
        channel_buttons_layout.addWidget(self.lock_button)
        channel_buttons_layout.addWidget(self.refresh_button)

        # serch line layout
        search_line_layout = QtWidgets.QHBoxLayout()
        self.search_lineEdit.setStyleSheet(line_edit_style)
        search_line_layout.addWidget(self.search_label)
        search_line_layout.addWidget(self.search_lineEdit)
        search_line_layout.addWidget(self.search_clear_button)

        # Buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addLayout(key_buttons_layout)
        # buttons_layout.addLayout(search_line_layout)
        buttons_layout.addStretch()
        buttons_layout.addLayout(channel_buttons_layout)

        main_layout.addLayout(search_line_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.tab_widget)

        # table layout TEMP
        main_table = QtWidgets.QTableWidget(self)
        main_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                 QtWidgets.QSizePolicy.Expanding)
        main_table.setColumnCount(3)
        main_table.verticalHeader().setVisible(False)
        main_table.horizontalHeader().setVisible(False)
        header_view = main_table.horizontalHeader()
        main_table.setStyleSheet(table_style)

        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header_view.resizeSection(0, 80)
        header_view.resizeSection(1, 17)

        i = 0
        for k in self.attrs["_attrs"]:
            at = self.attrs[k]
            if at["type"] in cmu.ATTR_SLIDER_TYPES:
                ctl = pm.selected()[0].name()
                val = cmds.getAttr(ctl + "." + k)
                sld = pyflow_widgets.pyf_Slider(self,
                                                defaultValue=val,
                                                sliderRange=(at["min"],
                                                             at["max"]))

                label = QtWidgets.QLabel(at["niceName"] + "  ")
                label.setMinimumWidth(80)
                label.setMaximumWidth(80)
                label.setToolTip(at["longName"])
                label.setAlignment(QtCore.Qt.AlignBottom
                                   | QtCore.Qt.AlignRight)

                button = QtWidgets.QPushButton()
                button.setMaximumHeight(17)
                button.setMinimumHeight(17)
                button.setMaximumWidth(17)
                button.setMinimumWidth(17)
                # button.setIcon(pyqt.get_icon("unlock", 11))
                button.setCheckable(True)

                main_table.insertRow(i)
                main_table.setRowHeight(i, 17)
                main_table.setCellWidget(i, 0, label)
                main_table.setCellWidget(i, 1, button)
                main_table.setCellWidget(i, 2, sld)
                i += 1

                # button.clicked.connect(partial(self.changeIcon, button))

        self.tab_widget.addTab(main_table, "Main")
        self.tab_widget.insertTab(1, QtWidgets.QPushButton(), "dos")
        self.tab_widget.insertTab(6, QtWidgets.QPushButton(), "new name")
        # main_layout.addStretch()

    def create_connections(self):
        pass

    def refresh_channels(self):
        pass



if __name__ == "__main__":

    from mgear.animbits import channel_master_utils
    reload(channel_master_utils)
    from mgear.animbits import channel_master_widgets
    reload(channel_master_widgets)
    from mgear.animbits import channel_master
    reload(channel_master)


    start = timeit.default_timer()

    ctl = pm.selected()[0].name()
    attrs = channel_master_utils.get_attributes_config(ctl)

    pyqt.showDialog(partial(channel_master.ChannelMaster, attrs),
                    dockable=True)

    end = timeit.default_timer()
    timeConsumed = end - start
    print "{} time elapsed running".format(timeConsumed)