import maya.cmds as cmds
import pymel.core as pm
from mgear.core import pyflow_widgets
from mgear.vendor.Qt import QtGui, QtCore, QtWidgets
import timeit


DEFAULT_RANGE = 1000
ATTR_SLIDER_TYPES = ["int", "float", "double", "doubleLinear", "doubleAngle"]


def get_keyable_attribute(node):
    """Get keyable attributes from node

    Args:
        node (str): name of the node that have the attribute

    Returns:
        list: list of keyable attributes
    """
    attrs = cmds.listAttr(node, ud=False, k=True)

    return attrs


def get_single_attribute_config(node, attr):
    """Summary

    Args:
        node (str): name of the node that have the attribute
        attr (str): attribute name

    Returns:
        dict: attribute configuration
    """
    config = {}
    config["type"] = cmds.attributeQuery(attr, node=node, attributeType=True)
    config["niceName"] = cmds.attributeQuery(attr, node=node, niceName=True)
    config["longName"] = cmds.attributeQuery(attr, node=node, longName=True)
    if config["type"] in ATTR_SLIDER_TYPES:
        if cmds.attributeQuery(attr, node=node, maxExists=True):
            config["max"] = cmds.attributeQuery(attr, node=node, max=True)[0]
        else:
            config["max"] = DEFAULT_RANGE
        if cmds.attributeQuery(attr, node=node, minExists=True):
            config["min"] = cmds.attributeQuery(attr, node=node, min=True)[0]
        else:
            config["min"] = DEFAULT_RANGE * -1
        config["default"] = cmds.attributeQuery(attr,
                                                node=node,
                                                listDefault=True)[0]
    elif config["type"] in ["enum"]:
        config["items"] = cmds.attributeQuery(attr, node=node, listEnum=True)

    return config


def get_attributes_config(node):
    """Get the configuration to all the keyable attributes

    Args:
        node (str): name of the node that have the attribute

    Returns:
        dict: All keyable attributes configuration
    """
    attrs_config = {}
    attrs_config["_attrs"] = get_keyable_attribute(node)
    for attr in attrs_config["_attrs"]:
        config = get_single_attribute_config(node, attr)
        attrs_config[attr] = config

    return attrs_config


def refresh_channel_value():
    # refresh channel value, after creation or scene manipulation
    # should be deactivate when playback, timeline scroll, etc
    pass


if __name__ == "__main__":

    start = timeit.default_timer()

    ctl = pm.selected()[0].name()
    attrs = get_attributes_config(ctl)

    class slider_dialog(QtWidgets.QDialog):

        def __init__(self, attrs, parent=None):
            super(slider_dialog, self).__init__(parent)
            self.deleteLater = True
            self.attrs = attrs

            self.setWindowTitle("slider test dialog")
            self.setMinimumWidth(200)
            flags = self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint
            self.setWindowFlags(flags)

            self.create_widgets()
            self.create_layout()

        def create_widgets(self):
            pass

        def create_layout(self):

            table_style = """
            QLabel{
                background: transparent;
                border: 0 solid transparent;
                color: #c8c8c8;
            }
            QTableView {
               border: 0 solid transparent;
            }

            """

            main_layout = QtWidgets.QVBoxLayout(self)
            main_table = QtWidgets.QTableWidget(self)
            main_table.setColumnCount(3)
            main_table.verticalHeader().setVisible(False)
            main_table.horizontalHeader().setVisible(False)
            header_view = main_table.horizontalHeader()
            main_table.setStyleSheet(table_style)

            header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            header_view.resizeSection(0,80)
            header_view.resizeSection(1,17)
            # main_table.setRowCount(20)

            i =0
            for k in attrs["_attrs"]:
                at = attrs[k]
                if at["type"] in ATTR_SLIDER_TYPES:
                    # channel_layout = QtWidgets.QHBoxLayout(self)
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
                    # channel_layout.addWidget(label)
                    # channel_layout.addWidget(button)
                    # channel_layout.addWidget(sld)
                    # channel_layout.setContentsMargins(0, 0, 0, 0)

                    main_table.insertRow(i)
                    main_table.setRowHeight(i, 17)
                    main_table.setCellWidget(i, 0, label)
                    main_table.setCellWidget(i, 1, button)
                    main_table.setCellWidget(i, 2, sld)
                    i+=1
            main_layout.addWidget(main_table)
            # main_layout.addStretch()

            main_layout.setContentsMargins(2, 2, 2, 2)
            main_layout.setSpacing(0)

    d = slider_dialog(attrs)

    d.show()

    end = timeit.default_timer()
    timeConsumed = end - start
    print "{} time elapsed running".format(timeConsumed)
