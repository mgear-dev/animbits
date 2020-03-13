import maya.cmds as cmds
import pymel.core as pm
from mgear.core import pyflow_widgets
from mgear.core import pyqt
from mgear.vendor.Qt import QtWidgets
from mgear.vendor.Qt import QtCore
from mgear.vendor.Qt import QtGui
import timeit
from functools import partial

from . import channel_master_utils as cmu


TABLE_STYLE = """
        QTableView {
           border: 0 solid transparent;
        }
        """

CHECKBOX_STYLE = """
        QCheckBox {
            background-color: #3C3C3C;
        }
        QWidget {
            background-color: #3C3C3C;
        }

        """


##################
# Helper functions
##################

def create_button(size=17,
                  text=None,
                  icon=None,
                  toggle_icon=None,
                  icon_size=None,
                  toolTip=None):
    """Create and configure a QPsuhButton

    Args:
        size (int, optional): Size of the button
        text (str, optional): Text of the button
        icon (str, optional): Icon name
        toggle_icon (str, optional): Toggle icon name. If exist will make
                                     the button checkable
        icon_size (int, optional): Icon size
        toolTip (str, optional): Buttom tool tip

    Returns:
        QPushButton: The reated button
    """
    button = QtWidgets.QPushButton()
    button.setMaximumHeight(size)
    button.setMinimumHeight(size)
    button.setMaximumWidth(size)
    button.setMinimumWidth(size)

    if toolTip:
        button.setToolTip(toolTip)

    if text:
        button.setText(text)

    if icon:
        if not icon_size:
            icon_size = size - 3
        button.setIcon(pyqt.get_icon(icon, icon_size))

    if toggle_icon:

        button.setCheckable(True)

        def changeIcon(button=button,
                       icon=icon,
                       toggle_icon=toggle_icon,
                       size=icon_size):
            if button.isChecked():
                button.setIcon(pyqt.get_icon(toggle_icon, size))
            else:
                button.setIcon(pyqt.get_icon(icon, size))

        button.clicked.connect(changeIcon)

    return button


def value_equal_keyvalue(attr, current_time=False):
    """Compare the animation value and the current value of a given attribute

    Args:
        attr (str): the attribute fullName

    Returns:
        bool: Return true is current value and animation value are the same
    """
    anim_val = cmu.get_anim_value_at_current_frame(attr)
    if current_time:
        val = cmds.getAttr(attr, time=current_time)
    else:
        val = cmds.getAttr(attr)
    if anim_val == val:
        return True


def refresh_key_button_color(button, attr, current_time=False):
    """refresh the key button color based on the animation of a given attribute

    Args:
        button (QPushButton): The button to update the color
        attr (str): the attribute fullName
    """
    if cmu.channel_has_animation(attr):
        if value_equal_keyvalue(attr, current_time):
            if cmu.current_frame_has_key(attr):
                button.setStyleSheet(
                    'QPushButton {background-color: #ce5846;}')
            else:
                button.setStyleSheet(
                    'QPushButton {background-color: #89bf72;}')
        else:
            button.setStyleSheet(
                'QPushButton {background-color: #ddd87c;}')

    else:
        button.setStyleSheet(
            'QPushButton {background-color: #ABA8A6;}')


def create_key_button(item_data):
    """Create a keyframing button

    Args:
        item_data (dict): Attribute channel configuration dictionary

    Returns:
        QPushButton: The keyframe button
    """
    button = create_button()
    attr = item_data["fullName"]
    refresh_key_button_color(button, attr)

    # right click menu
    pop_menu = QtWidgets.QMenu(button)

    next_key_action = QtWidgets.QAction('Next Keyframe', button)
    next_key_action.setIcon(pyqt.get_icon("arrow-right"))
    next_key_action.triggered.connect(partial(cmu.next_keyframe, attr))
    pop_menu.addAction(next_key_action)

    previous_key_action = QtWidgets.QAction('previous Keyframe', button)
    previous_key_action.setIcon(pyqt.get_icon("arrow-left"))
    previous_key_action.triggered.connect(partial(cmu.previous_keyframe, attr))
    pop_menu.addAction(previous_key_action)

    pop_menu.addSeparator()

    remove_animation_action = QtWidgets.QAction('Remove Animation', button)
    remove_animation_action.setIcon(pyqt.get_icon("trash"))
    remove_animation_action.triggered.connect(
        partial(cmu.remove_animation, attr))
    pop_menu.addAction(remove_animation_action)

    def context_menu(point):
        pop_menu.exec_(button.mapToGlobal(point))

    button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    button.customContextMenuRequested.connect(context_menu)

    def button_clicked():
        if cmu.current_frame_has_key(attr) and value_equal_keyvalue(attr):
            cmu.remove_key(attr)

        else:
            cmu.set_key(attr)

        refresh_key_button_color(button, attr)

    button.clicked.connect(button_clicked)

    return button


###################################################
# Channel Table Class
###################################################


class ChannelTable(QtWidgets.QTableWidget):

    def __init__(self, attrs_config, parent=None):
        super(ChannelTable, self).__init__(parent)
        self.attrs_config = attrs_config
        self.trigger_value_update = True
        self.track_widgets = []
        self.create_menu()
        self.setup_table()
        self.config_table()

    def create_menu(self):
        self.menu = QtWidgets.QMenu(self)

        set_color_action = QtWidgets.QAction('Set Color', self)
        set_color_action.setIcon(pyqt.get_icon("edit-2"))
        set_color_action.triggered.connect(self.set_color_slot)
        self.menu.addAction(set_color_action)

        clear_color_action = QtWidgets.QAction('Clear Color', self)
        clear_color_action.setIcon(pyqt.get_icon("x-octagon"))
        clear_color_action.triggered.connect(self.clear_color_slot)
        self.menu.addAction(clear_color_action)
        self.menu.addSeparator()

        # if there is no slider in the selected item will print  an info msg
        set_range_action = QtWidgets.QAction('Set Range', self)
        set_range_action.setIcon(pyqt.get_icon("sliders"))
        set_range_action.triggered.connect(self.set_range_slot)
        self.menu.addAction(set_range_action)
        self.menu.addSeparator()

        reset_value_action = QtWidgets.QAction('Reset Value to Default', self)
        reset_value_action.setIcon(pyqt.get_icon("rewind"))
        reset_value_action.triggered.connect(self.reset_value_slot)
        self.menu.addAction(reset_value_action)

    def set_color_slot(self):
        items = self.selectedItems()
        if items:
            color = QtWidgets.QColorDialog.getColor(
                items[0].background().color(),
                parent=self,
                options=QtWidgets.QColorDialog.DontUseNativeDialog)
            if not color.isValid():
                return

            for itm in items:
                itm.setBackground(color)

    def reset_value_slot(self):
        items = self.selectedItems()
        if items:
            for itm in items:
                attr_config = itm.data(QtCore.Qt.UserRole)
                cmu.reset_attribute(attr_config)


    def clear_color_slot(self):
        items = self.selectedItems()
        if items:
            for itm in items:
                itm.setBackground(QtGui.QColor(43, 43, 43))

    def set_range_slot(self):
        items = self.selectedItems()
        if items:
            init_range = None
            for itm in items:
                attr = itm.data(QtCore.Qt.UserRole)
                if attr["type"] in cmu.ATTR_SLIDER_TYPES:
                    ch_item = self.cellWidget(itm.row(), 2)
                    if not init_range:
                        init_range = ch_item.getRange()
                        set_range_dialog = SetRangeDialog(init_range,
                                                          self)
                        result = set_range_dialog.exec_()

                        if result != QtWidgets.QDialog.Accepted:
                            return
                    new_range = set_range_dialog.get_range()
                    ch_item.setRange(new_range[0], new_range[1])

    def setup_table(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self.setColumnCount(3)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        header_view = self.horizontalHeader()
        self.setStyleSheet(TABLE_STYLE)

        header_view.resizeSection(0, 80)
        header_view.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        header_view.resizeSection(1, 17)
        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    def contextMenuEvent(self, event):
        if self.selectedItems():

            self.menu.popup(QtGui.QCursor.pos())

    def config_table(self):

        def value_update(attr_config, *args):
            """Update the attribute from the  channel value

            Args:
                ch (QWidget): The channel widget
                atttr_config (dict): attribute configuration data
                *args: the current value
            """
            if self.trigger_value_update:
                cmds.setAttr(attr_config["fullName"], args[0])

                # refresh button color while value update
                for i in xrange(self.rowCount()):
                    item = self.item(i, 0)
                    attr = item.data(QtCore.Qt.UserRole)
                    if attr["fullName"] == attr_config["fullName"]:
                        button = self.cellWidget(i, 1)
                        refresh_key_button_color(button,
                                                 attr_config["fullName"])
                        break

        def open_undo_chunk():
            cmds.undoInfo(openChunk=True)

        def close_undo_chunk():
            cmds.undoInfo(closeChunk=True)

        if not self.attrs_config:
            return

        i = 0
        for k in self.attrs_config["_attrs"]:
            at = self.attrs_config[k]
            ctl = at["ctl"]
            val = cmds.getAttr(ctl + "." + k)
            if at["type"] in cmu.ATTR_SLIDER_TYPES:
                if at["type"] == "long":
                    Type = "int"
                else:
                    Type = "float"
                ch_ctl = pyflow_widgets.pyf_Slider(self,
                                                   Type=Type,
                                                   defaultValue=val,
                                                   sliderRange=(at["min"],
                                                                at["max"]))

                ch_ctl.valueChanged.connect(
                    partial(value_update, at))
                ch_ctl.sliderPressed.connect(open_undo_chunk)
                ch_ctl.sliderReleased.connect(close_undo_chunk)

            elif at["type"] == "bool":

                ch_ctl = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout(ch_ctl)
                cbox = QtWidgets.QCheckBox()
                cbox.setStyleSheet(CHECKBOX_STYLE)
                ch_ctl.setStyleSheet(CHECKBOX_STYLE)
                layout.addWidget(cbox)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                ch_ctl.setLayout(layout)
                if val:
                    cbox.setChecked(True)

                cbox.toggled.connect(
                    partial(value_update, at))

            elif at["type"] == "enum":

                # we handle special naming for separators
                if at["niceName"] == "__________":
                    continue
                else:
                    ch_ctl = QtWidgets.QComboBox()
                    ch_ctl.addItems(at["items"])
                    ch_ctl.setCurrentIndex(val)

                    ch_ctl.currentIndexChanged.connect(
                        partial(value_update, at))

            label_item = QtWidgets.QTableWidgetItem(at["niceName"] + "  ")
            label_item.setData(QtCore.Qt.UserRole, at)
            label_item.setTextAlignment(QtCore.Qt.AlignRight)
            label_item.setToolTip(at["fullName"])
            label_item.setFlags(label_item.flags() ^ QtCore.Qt.ItemIsEditable)

            key_button = create_key_button(at)

            self.insertRow(i)
            self.setRowHeight(i, 17)
            self.setItem(i, 0, label_item)
            self.setCellWidget(i, 1, key_button)
            self.setCellWidget(i, 2, ch_ctl)

            self.track_widgets.append([key_button, ch_ctl])

            i += 1

    def update_table(self):
        """Update the  table with the channels of the selected object
        If multiple objects are selected. Only the las selected will be listed
        """
        self.clear()
        for i in xrange(self.rowCount()):
            self.removeRow(0)

        for x in self.track_widgets:
            x[0].deleteLater()
            x[1].deleteLater()

        self.track_widgets = []

        self.attrs_config = cmu.get_table_config_from_selection()
        self.config_table()

    def refresh_channels_values(self, current_time=False):
        """refresh the channel values of the table
        """
        self.trigger_value_update = False
        for i in xrange(self.rowCount()):
            ch_item = self.cellWidget(i, 2)
            item = self.item(i, 0)
            attr = item.data(QtCore.Qt.UserRole)
            if current_time:
                # Note: we can not set time to False because looks like
                # having this flag force the evaluation on the animation
                # curve and not in the current attribute value
                val = cmds.getAttr(attr["fullName"], time=current_time)
            else:
                val = cmds.getAttr(attr["fullName"])
            if attr["type"] in cmu.ATTR_SLIDER_TYPES:
                ch_item.setValue(val)
            elif attr["type"] == "bool":
                if val:
                    cbox = ch_item.findChildren(QtWidgets.QCheckBox)[0]
                    cbox.setChecked(True)
            elif attr["type"] == "enum":
                ch_item.setCurrentIndex(val)

            # refresh button color
            button_item = self.cellWidget(i, 1)
            refresh_key_button_color(button_item,
                                     attr["fullName"],
                                     current_time)

        self.trigger_value_update = True


##################
# set range dialog
##################


class SetRangeDialog(QtWidgets.QDialog):
    """
    Set range dialog
    """

    def __init__(self, init_range=None, parent=None):
        super(SetRangeDialog, self).__init__(parent)

        self.setWindowTitle("Set Range")
        flags = self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)

        self.init_range = init_range

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.min_spinbox = QtWidgets.QDoubleSpinBox()
        self.min_spinbox.setFixedWidth(80)
        self.min_spinbox.setMinimum(-1000000)
        self.min_spinbox.setMaximum(1000000)
        self.max_spinbox = QtWidgets.QDoubleSpinBox()
        self.max_spinbox.setMinimum(-1000000)
        self.max_spinbox.setMaximum(1000000)
        self.max_spinbox.setFixedWidth(80)
        if self.init_range:
            self.min_spinbox.setValue(self.init_range[0])
            self.max_spinbox.setValue(self.init_range[1])

        self.ok_btn = QtWidgets.QPushButton("OK")

    def create_layout(self):
        wdg_layout = QtWidgets.QHBoxLayout()
        wdg_layout.addWidget(QtWidgets.QLabel("Min: "))
        wdg_layout.addWidget(self.min_spinbox)
        wdg_layout.addWidget(QtWidgets.QLabel("Max: "))
        wdg_layout.addWidget(self.max_spinbox)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(wdg_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.ok_btn.clicked.connect(self.accept)

    def get_range(self):
        return([self.min_spinbox.value(),
                self.max_spinbox.value()])
