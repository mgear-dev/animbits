import json
import ast
from maya import cmds
import pymel.core  as pm

from mgear.core import attribute

from . import channel_master_utils as cmu


__TAG__ = "_isChannelMasterNode"

# TODO: Node should store the current active tab

def list_channel_master_nodes():
    """return a list of channel master nodes in the scene

    Returns:
        list: List of channel master nodes
    """
    return [n for n in cmds.ls("*.{}".format(__TAG__), o=True, r=True)]


def create_channel_master_node(name):
    """Create a new channel master node

    Args:
        name (str): name of the nodes

    Returns:
        str: name of the channel master node
    """

    # Create data node (render sphere for outliner "icon")
    shp = cmds.createNode("renderSphere")
    cmds.setAttr("{}.radius".format(shp), 0)
    cmds.setAttr("{}.isHistoricallyInteresting".format(shp), 0)
    cmds.setAttr("{}.v".format(shp), 0)

    # Rename data node
    node = cmds.listRelatives(shp, p=True)[0]
    node = cmds.rename(node, name)

    cmds.addAttr(node, ln=__TAG__, at="bool", dv=True)
    cmds.setAttr("{}.{}".format(node, __TAG__), k=False, l=True)
    cmds.addAttr(node, ln="data", dt="string")

    attribute.lockAttribute(pm.PyNode(node))

    # init data
    cmds.setAttr("{}.data".format(node),
                 cmu.init_channel_master_config_data(),
                 type="string")
    return node


def get_node_data(node):
    data = cmds.getAttr("{}.data".format(node))
    return ast.literal_eval(data)


def set_node_data(node, data):
    cmds.setAttr("{}.data".format(node), data, type="string")


def export_data(node):
    pass


def import_data(node):
    pass
