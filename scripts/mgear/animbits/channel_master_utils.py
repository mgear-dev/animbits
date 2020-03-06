import maya.cmds as cmds


ATTR_SLIDER_TYPES = ["long", "float", "double", "doubleLinear", "doubleAngle"]
DEFAULT_RANGE = 1000


# TODO: filter channel by color. By right click menu in a channel with color

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
    config["ctl"] = node
    config["color"] = None # This is a place holder for the channel UI color
    config["type"] = cmds.attributeQuery(attr, node=node, attributeType=True)
    config["niceName"] = cmds.attributeQuery(attr, node=node, niceName=True)
    config["longName"] = cmds.attributeQuery(attr, node=node, longName=True)
    config["fullName"] = config["ctl"] + "." + config["longName"]
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
        items = cmds.attributeQuery(attr, node=node, listEnum=True)[0]

        config["items"] = [x for x in items.split(":")]

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
