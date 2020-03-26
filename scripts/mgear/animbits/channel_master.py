import maya.cmds as cmds
import pymel.core as pm
from mgear.core import pyqt
from mgear.vendor.Qt import QtWidgets
from mgear.vendor.Qt import QtCore
from mgear.vendor.Qt import QtGui
from mgear.core import callbackManager
import timeit
from functools import partial
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


from . import channel_master_utils as cmu
from . import channel_master_widgets as cmw
from . import channel_master_node as cmn


class ChannelMaster(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(ChannelMaster, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.setWindowTitle("Channel Master")
        min_w = 155
        default_w = 250
        default_h = 600
        self.setMinimumWidth(min_w)
        self.resize(default_w, default_h)
        if cmds.about(ntOS=True):
            flags = self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
            self.setWindowFlags(flags)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.values_buffer = []

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, 1)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.refresh_channels_values()

        self.cb_manager = callbackManager.CallbackManager()

        self.add_callback()

    def add_callback(self):
        self.cb_manager.selectionChangedCB("Channel_Master_selection_CB",
                                           self.selection_change)
        self.cb_manager.userTimeChangedCB("Channel_Master_userTimeChange_CB",
                                          self.time_changed)

    def enterEvent(self, evnt):
        self.refresh_channels_values()

    def close(self):
        self.cb_manager.removeAllManagedCB()
        self.deleteLater()

    def closeEvent(self, evnt):
        self.close()

    def dockCloseEventTriggered(self):
        self.close()

    def create_actions(self):
        # file actions
        self.file_new_node_action = QtWidgets.QAction("New Node", self)
        self.file_new_node_action.setIcon(pyqt.get_icon("plus-square"))
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
        self.tab_rename_action = QtWidgets.QAction("Rename Tab", self)
        # self.tab_rename_action.setIcon(pyqt.get_icon("copy"))

    def create_widgets(self):
        # Menu bar
        self.menu_bar = QtWidgets.QMenuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(self.file_new_node_action)
        self.file_menu.addSeparator()
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
        self.tab_menu.addAction(self.tab_rename_action)
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

        # node list widgets
        self.node_list_combobox = QtWidgets.QComboBox()
        self.node_list_combobox.setMaximumHeight(17)
        self.refresh_node_list_button = cmw.create_button(
            size=17, icon="list", toolTip="Refresh Node List")
        self.new_node_button = cmw.create_button(
            size=17,
            icon="plus-square",
            toolTip="Create New Channel Master Node")
        self.refresh_node_list()

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

        # Init Main Channels table
        self.main_table = cmw.ChannelTable(
            cmu.get_table_config_from_selection(), self)

    def create_layout(self):

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
        key_buttons_layout = QtWidgets.QHBoxLayout()
        key_buttons_layout.addWidget(self.key_all_button)
        key_buttons_layout.addWidget(self.key_copy_button)
        key_buttons_layout.addWidget(self.key_paste_button)

        # channel listing buttons Layout
        channel_add_remove_buttons_layout = QtWidgets.QVBoxLayout()
        channel_add_remove_buttons_layout.addWidget(self.add_channel_button)
        channel_add_remove_buttons_layout.addWidget(self.remove_channel_button)
        channel_buttons_layout = QtWidgets.QHBoxLayout()
        channel_buttons_layout.addLayout(channel_add_remove_buttons_layout)
        channel_buttons_layout.addWidget(self.lock_button)
        channel_buttons_layout.addWidget(self.refresh_button)

        # node list layout
        node_list_layout = QtWidgets.QHBoxLayout()
        node_list_layout.addWidget(self.node_list_combobox)
        node_list_layout.addWidget(self.refresh_node_list_button)
        node_list_layout.addWidget(self.new_node_button)

        # serch line layout
        search_line_layout = QtWidgets.QHBoxLayout()
        self.search_lineEdit.setStyleSheet(line_edit_style)
        search_line_layout.addWidget(self.search_label)
        search_line_layout.addWidget(self.search_lineEdit)
        search_line_layout.addWidget(self.search_clear_button)

        # Buttons layout
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addLayout(key_buttons_layout)
        buttons_layout.addStretch()
        buttons_layout.addLayout(channel_buttons_layout)

        main_layout.addLayout(node_list_layout)
        main_layout.addLayout(search_line_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.tab_widget)

        # main_table
        self.tab_widget.addTab(self.main_table, "Main")

    def create_connections(self):
        #  actions File
        self.file_new_node_action.triggered.connect(
            self.create_new_node)

        # actions display
        self.display_fullname_action.triggered.connect(
            self.action_display_fullname)
        self.display_order_default_action.triggered.connect(
            self.action_default_order)
        self.display_order_alphabetical_action.triggered.connect(
            self.action_alphabetical_order)

        # action tab
        self.tab_new_action.triggered.connect(self.add_tab)
        self.tab_del_action.triggered.connect(self.delete_tab)
        self.tab_dup_action.triggered.connect(self.duplicate_tab)
        self.tab_rename_action.triggered.connect(self.rename_tab)

        # Buttons
        self.search_lineEdit.textChanged.connect(self.search_channels)
        self.search_clear_button.clicked.connect(self.search_clear)

        self.refresh_button.clicked.connect(self.update_main_table)

        self.key_all_button.clicked.connect(self.key_all)
        self.key_copy_button.clicked.connect(self.copy_all_values)
        self.key_paste_button.clicked.connect(self.paste_all_values)

        self.refresh_node_list_button.clicked.connect(self.refresh_node_list)
        self.new_node_button.clicked.connect(self.create_new_node)

        self.add_tab_button.clicked.connect(self.add_tab)

    def get_current_table(self):
        """get the active channel table for active tab

        Returns:
            QTableWidget: the channel table widget
        """
        tab = self.tab_widget.currentIndex()
        table = self.tab_widget.widget(tab)
        return table

    def get_all_tables(self):
        return

    def update_main_table(self):
        # TODO: add confirmation box if lock button is pressed
        self.main_table.update_table()
        # Clean values buffer
        self.values_buffer = []

    def search_channels(self):
        """Filter the visible rows in the channel table.
        NOTE: ideally this should be implemented with a model/view pattern
        using QTableView
        """
        search_name = self.search_lineEdit.text()
        table = self.get_current_table()
        for i in xrange(table.rowCount()):
            item = table.item(i, 0)
            if search_name.lower() in item.text().lower() or not search_name:
                table.setRowHidden(i, False)
            else:
                table.setRowHidden(i, True)

    def search_clear(self):
        """Clear search field
        """
        self.search_lineEdit.setText("")

    def refresh_channels_values(self, current_time=False):
        """Refresh the channel values of the current table
        """
        table = self.get_current_table()
        if table:
            table.refresh_channels_values(current_time)

    # actions
    def action_display_fullname(self):
        """Toggle channel name  from nice name to full name
        """
        table = self.get_current_table()
        for i in xrange(table.rowCount()):
            table.set_channel_fullname(
                i, self.display_fullname_action.isChecked())

    def action_default_order(self):

        # table = self.get_current_table()
        print "Need to be implemented from the node stored order"

    def action_alphabetical_order(self):

        table = self.get_current_table()
        table.sortItems(0, order=QtCore.Qt.AscendingOrder)

    # callback slots
    def selection_change(self, *args):
        if not self.lock_button.isChecked():
            self.update_main_table()

    def time_changed(self, *args):
        self.refresh_channels_values(current_time=pm.currentTime())

    # Keyframe

    def key_all(self, *args):
        table = self.get_current_table()
        not_keyed = []
        keyed = []
        for i in xrange(table.rowCount()):
            item = table.item(i, 0)
            attr = item.data(QtCore.Qt.UserRole)["fullName"]
            if cmu.current_frame_has_key(attr) \
                    and cmu.value_equal_keyvalue(attr):
                keyed.append(attr)
            else:
                not_keyed.append(attr)

        if not_keyed:
            cmu.set_key(not_keyed)
        else:
            cmu.remove_key(keyed)

        self.refresh_channels_values()

    def copy_all_values(self, *args):
        """Copy all attribute values from curretn channel table

        Args:
            *args: Description
        """
        table = self.get_current_table()
        self.values_buffer = []
        for i in xrange(table.rowCount()):
            item = table.item(i, 0)
            attr = item.data(QtCore.Qt.UserRole)
            self.values_buffer.append(cmds.getAttr(attr["fullName"]))

    def paste_all_values(self, *args):
        """Paste and key values stored in buffer

        Args:
            *args: Description

        Returns:
            None: Return none if no values stored in buffer
        """
        if not self.values_buffer:
            return
        table = self.get_current_table()
        for i in xrange(table.rowCount()):
            item = table.item(i, 0)
            attr = item.data(QtCore.Qt.UserRole)
            cmds.setAttr(attr["fullName"], self.values_buffer[i])
            cmu.set_key(attr["fullName"])

        self.refresh_channels_values()

    def refresh_node_list(self):
        """Refresh the channel master node list
        """
        nodes = cmn.list_channel_master_nodes()
        nodes.reverse()
        self.node_list_combobox.clear()
        self.node_list_combobox.addItems(nodes)

    def create_new_node(self):
        """Create a new node

        Returns:
            bool: return false if the dialog is not accepted
        """
        sel = pm.selected()
        new_node_dialog = cmw.CreateChannelMasterNodeDialog(self)
        result = new_node_dialog.exec_()
        if result != QtWidgets.QDialog.Accepted:
            return
        name = new_node_dialog.get_name()
        if name:
            node = cmn.create_channel_master_node(name)
            self.refresh_node_list()
            for i in xrange(self.node_list_combobox.count()):
                if self.node_list_combobox.itemText(i) == node:
                    self.node_list_combobox.setCurrentIndex(i)
                    break
            pm.select(sel)

        else:
            pm.displayWarning("No valid node name!")

    def add_tab(self):
        """Add new tab to the channel master

        Returns:
            bood: False if not accepted
        """
        new_tab_dialog = cmw.CreateChannelMasterTabDialog(self)
        result = new_tab_dialog.exec_()
        if result != QtWidgets.QDialog.Accepted:
            return
        name = new_tab_dialog.get_name()
        if name:
            name = self.check_tab_name(name)
            new_table = cmw.ChannelTable(None, self)
            self.tab_widget.addTab(new_table, name)
            self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
        else:
            pm.displayWarning("No valid tab name!")


    def duplicate_tab(self):
        pass

    def delete_tab(self):
        cur_idx = self.tab_widget.currentIndex()
        if cur_idx >= 1:
            button_pressed = QtWidgets.QMessageBox.question(
                self, "Delete Tab", "Confirm Delete Tab?")
            if button_pressed == QtWidgets.QMessageBox.Yes:
                page = self.tab_widget.widget(cur_idx)
                self.tab_widget.removeTab(cur_idx)
                page.deleteLater()
        else:
            pm.displayWarning("Main Tab Can't be deleted!")

    def check_tab_name(self, name):
        """Check if the tab name is unique and add an index if not

        Args:
            name (str): Name to check

        Returns:
            str: unique name after check
        """
        init_name = name
        names = []
        for i in xrange(self.tab_widget.count()):
            names.append(self.tab_widget.tabText(i))
        i = 1
        while name in names:
            name = init_name + str(i)
            i += 1

        return name

    def rename_tab(self):
        cur_idx = self.tab_widget.currentIndex()
        if cur_idx >= 1:
            new_tab_dialog = cmw.CreateChannelMasterTabDialog(self)
            result = new_tab_dialog.exec_()
            if result != QtWidgets.QDialog.Accepted:
                return
            name = new_tab_dialog.get_name()
            if name:
                name = self.check_tab_name(name)
                self.tab_widget.setTabText(cur_idx, name)

            else:
                pm.displayWarning("No valid tab name!")
        else:
            pm.displayWarning("Main Tab Can't be renamed!")


    def add_channels_to_current_tab(self):
        pass

    def remove_selected_channels(self):
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
