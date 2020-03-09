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


class ChannelTable(QtWidgets.QTableWidget):

    def __init__(self, attrs_config, parent=None):
        super(ChannelTable, self).__init__(parent)
        self.attrs_config = attrs_config
        self.trigger_value_update = True
        self.setup_table()
        self.config_table()
        self.update_table()

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

    def config_table(self):

        def value_update(atttr_config, *args):
            """Update the attribute from the  channel value

            Args:
                ch (QWidget): The channel widget
                atttr_config (dict): attribute configuration data
                *args: the current value
            """
            if self.trigger_value_update:
                cmds.setAttr(atttr_config["fullName"], args[0])

        def open_undo_chunk():
            cmds.undoInfo(openChunk=True)

        def close_undo_chunk():
            cmds.undoInfo(closeChunk=True)


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

            # print label_item.data(QtCore.Qt.UserRole)

            key_button = create_button()

            self.insertRow(i)
            self.setRowHeight(i, 17)
            self.setItem(i, 0, label_item)
            self.setCellWidget(i, 1, key_button)
            self.setCellWidget(i, 2, ch_ctl)

            i += 1

    def update_table(self):
        pass
