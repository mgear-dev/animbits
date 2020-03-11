import maya.cmds as cmds
import pymel.core as pm


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
    config["color"] = None  # This is a place holder for the channel UI color
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
    keyable_attrs = get_keyable_attribute(node)
    if keyable_attrs:
        attrs_config["_attrs"] = keyable_attrs
        for attr in attrs_config["_attrs"]:
            config = get_single_attribute_config(node, attr)
            attrs_config[attr] = config

    return attrs_config


def refresh_channel_value():
    # refresh channel value, after creation or scene manipulation
    # should be deactivate when playback, timeline scroll, etc
    pass


def get_table_config_from_selection():
    oSel = pm.selected()
    attrs_config = {}
    if oSel:
        ctl = oSel[-1].name()
        attrs_config = get_attributes_config(ctl)

    return attrs_config


################
# Keyframe utils
################

def current_frame_has_key(attr):
    """Check if the attribute has keyframe in the current frame

    Args:
        attr (str): Attribute fullName

    Returns:
        bool: Return true if the attribute has keyframe in the current frame
    """
    k = pm.keyframe(attr, query=True, time=pm.currentTime())
    if k:
        return True


def channel_has_animation(attr):
    """Check if the current channel has animaton

    Args:
        attr (str): Attribute fullName

    Returns:
         bool: Return true if the attribute has animation
    """
    k = cmds.keyframe(attr, query=True)
    if k:
        return True


def get_anim_value_at_current_frame(attr):
    """Get the animation value in the current framwe from a given attribute

    Args:
        attr (str): Attribute fullName

    Returns:
        bol, int or float: animation current value
    """
    return cmds.keyframe(attr, query=True, eval=True)[0]


def set_key(attr):
    """Keyframes the attribute at current frame

    Args:
        attr (str): Attribute fullName
    """
    cmds.setKeyframe(attr)


def remove_key(attr):
    """Remove the keyframe of an attribute at current frame

    Args:
        attr (str): Attribute fullName
    """
    pm.cutKey(attr, clear=True, time=pm.currentTime())


def remove_animation(attr):
    """Remove the animation of an attribute

    Args:
        attr (str): Attribute fullName
    """
    pm.cutKey(attr, clear=True)

def _go_to_keyframe(attr, which):
    frame = cmds.findKeyframe(attr, which=which)
    cmds.currentTime(frame, e=True)

def next_keyframe(attr):
    _go_to_keyframe(attr, which="next")

def previous_keyframe(attr):
    _go_to_keyframe(attr, which="previous")
