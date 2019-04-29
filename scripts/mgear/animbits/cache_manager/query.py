
# imports
import os
from maya import cmds

# ==============================================================================
# CONSTANTS
# ==============================================================================

_MANAGER_RIG_ATTRIBUTE = os.getenv("MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE")
_MANAGER_CACHE_DESTINATION = os.getenv("MGEAR_CACHE_MANAGER_CACHE_DESTINATION")
# ==============================================================================


def get_scene_rigs():
    """ The rigs from current Maya session

    This method search for rigs in your current Maya scene.
    If the MGEAR_CACHE_MANAGER_RIG_ATTRIBUTE has been set it will try to find
    rigs based on the attribute set on the environment variable. Otherwise
    it will use the attribute **gear_version** in order to find rigs in scene.

    Returns:
        list: mGear rig top node or None
    """

    if not _MANAGER_RIG_ATTRIBUTE:
        rigs = [x.split(".")[0] for x in cmds.ls("*.gear_version",
                                                 recursive=True)]
    else:
        rigs = [x.split(".")[0] for x in cmds.ls(
            "*.{}".format(_MANAGER_RIG_ATTRIBUTE), recursive=True)]

    return rigs or None
