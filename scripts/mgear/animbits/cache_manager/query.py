
# imports
import os
from maya import cmds

# ==============================================================================
# CONSTANTS
# ==============================================================================

MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE = os.getenv(
    "MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE")


def get_scene_rigs():
    """ The rigs from current Maya session

    Returns:
        list: mGear rig top node or None
    """

    if not MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE:
        rigs = [x.split(".")[0] for x in cmds.ls("*.gear_version",
                                                 recursive=True)]
    else:
        rigs = [x.split(".")[0] for x in cmds.ls(
            "*.{}".format(MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE), recursive=True)]

    return rigs or None
