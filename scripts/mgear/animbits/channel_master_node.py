from maya import cmds
import pymel.core  as pm

from mgear.core import attribute


__TAG__ = "_isChannelMasterNode"


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
    fullName = name + "_channelMasterNode"

    # Create data node (render sphere for outliner "icon")
    shp = cmds.createNode("renderSphere")
    cmds.setAttr("{}.radius".format(shp), 0)
    cmds.setAttr("{}.isHistoricallyInteresting".format(shp), 0)
    cmds.setAttr("{}.v".format(shp), 0)

    # Rename data node
    node = cmds.listRelatives(shp, p=True)[0]
    node = cmds.rename(node, fullName)

    cmds.addAttr(node, ln=__TAG__, at="bool", dv=True)
    cmds.setAttr("{}.{}".format(node, __TAG__), k=False, l=True)
    cmds.addAttr(node, ln="data", dt="string")

    attribute.lockAttribute(pm.PyNode(node))
    return node


def get_node_data(node):
    pass


def set_node_data(node, data):
    pass


def export_data(node):
    pass


def import_data(node):
    pass
