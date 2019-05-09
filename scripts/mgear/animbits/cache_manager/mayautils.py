
# imports
from __future__ import absolute_import
import os
import re
import json
from maya import cmds, OpenMayaUI
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from mgear.animbits.cache_manager.query import _MANAGER_PREFERENCE_PATH
from mgear.animbits.cache_manager.query import get_preference_file
from mgear.animbits.cache_manager.query import get_cache_destination_path
from mgear.animbits.cache_manager.query import get_time_stamp


def __check_gpu_plugin():
    """ Check for the gpuCache plugin load
    """

    if not cmds.pluginInfo('gpuCache', query=True, loaded=True):
        cmds.loadPlugin('gpuCache')


def __create_preference_file():
    """ Creates the json file to store preferences for the cache manager

    The preference file is created inside the preference folder. It's placement
    is defined by the MAYA_APP_DIR environment variable and it's name by the
    _MANAGER_PREFERENCE_FILE constant

    Returns:
        str: Path to the preference file
    """

    try:
        # creates file
        pref_file = open(get_preference_file(), "w")

        # creates the data structure
        data = {}
        data["preferences"] = []
        data["preferences"].append({"cache_manager_cache_path": ""})
        data["preferences"].append({"cache_manager_model_group": ""})
        json.dump(data, pref_file, indent=4)
        pref_file.close()
        return pref_file.name
    except Exception as e:
        message = "Contact mGear's developers reporting this issue to get help"
        print("{} - {} / {}".format(type(e).__name__, e,
                                    message))


def __create_preference_folder():
    """ Creates the preference folder for the cache manager

    The preference folder gets created wherever the MAYA_APP_DIR environment
    variables points at.
    """

    try:
        os.makedirs(_MANAGER_PREFERENCE_PATH)
    except Exception as e:
        message = "Contact mGear's developers reporting this issue to get help"
        print("{} - {} / {}".format(type(e).__name__, e,
                                    message))


def __is_maya_batch():
    """ Returns if the current session is a Maya batch session or not

    Returns:
        bool: if Maya is on batch mode or not
    """

    return cmds.about(batch=True)


def create_cache_manager_preference_file():
    """ Creates the Animbits cache manager preference file

    Returns:
        str or None: Path to the preference file if existing or created one.
                     None if failed
    """

    pref_file = get_preference_file()

    if not os.path.exists(pref_file):
        __create_preference_folder()
        pref_file = __create_preference_file()

    return pref_file


def generate_gpu_cache(geo_node, cache_name, start, end, rig_node, lock=False):
    """ Generates a GPU representation for shapes found under the geo_node

    Args:
        geo_node (str): geometry group transform node containing the shapes to
                        cache
        cache_name (str): file name to use for the gpu cache file
        start (float): start frame to use
        end (float): end frame to use
        rig_node (str): Rig root node containing the geo_node
        lock (bool): Whether or not the gpu cache node should be locked
    """

    # checks for plugin load
    __check_gpu_plugin()

    # gets cache destination path
    cache_destination = get_cache_destination_path()

    try:
        file_name = re.sub('[^\w_.)( -]', '_', cache_name)
        file_name += "_{}".format(get_time_stamp())
        # Runs the GPU cache generation
        gpu_file = cmds.gpuCache("{}".format(geo_node),
                                 startTime=start,
                                 endTime=end,
                                 optimize=True,
                                 optimizationThreshold=4000,
                                 writeMaterials=True,
                                 directory=cache_destination,
                                 fileName=file_name,
                                 showStats=True,
                                 useBaseTessellation=False)

        # loads gpu cache
        gpu_node = cmds.createNode("gpuCache", name="{}_cacheShape"
                                   .format(cache_name))
        cmds.setAttr("{}.cacheFileName".format(gpu_node),
                     "{}".format(gpu_file[0]), type="string")

        # adds link attribute to rig
        cmds.addAttr(gpu_node, longName="rig_link", dataType="string")
        cmds.setAttr("{}.rig_link".format(gpu_node), "{}".format(rig_node),
                     type="string", lock=True)
        cmds.lockNode(gpu_node, lock=lock)

        return gpu_node

    except Exception as e:
        raise e


def install_script_job(function):
    """ Adds a script job for file read and scene opened
    """

    kill_script_job(function.__name__)
    cmds.scriptJob(event=["NewSceneOpened", function])
    cmds.scriptJob(conditionTrue=["readingFile", function])


def kill_script_job(name):
    """ Finds the given script job name and deletes it

    Args:
        name (str): the name for the script job to kill
    """

    for job in cmds.scriptJob(lj=True):
        if name in job:
            print("Killing script job {}".format(job))
            _id = int(job.split(":")[0])
            cmds.scriptJob(k=_id)


def kill_ui(name):
    """ Deletes an already created widget

    Args:
        name (str): the widget object name
    """

    # finds workspace control if dockable widget
    if cmds.workspaceControl(name, exists=True):
        cmds.workspaceControl(name, edit=True, clp=False)
        cmds.deleteUI(name)

    # finds the widget
    widget = OpenMayaUI.MQtUtil.findWindow(name)

    if not widget:
        return

    # wraps the widget into a qt object
    qt_object = wrapInstance(long(widget), QtWidgets.QDialog)

    # sets the widget parent to none
    qt_object.setParent(None)

    # deletes the widget
    qt_object.deleteLater()
    del(qt_object)


def set_preference_file_cache_destination(cache_path):
    """ Sets the Cache Manager cache destination path into the preference file

    Args:
        cache_path (str): The folder path for the cache files
    """

    # preference file
    pref_file = get_preference_file()

    try:
        # reads file
        pref_file = open(get_preference_file(), "r")

        # edits path
        data = json.load(pref_file)
        data["preferences"][0]["cache_manager_cache_path"] = cache_path
        pref_file.close()

        # writes file
        pref_file = open(get_preference_file(), "w")
        json.dump(data, pref_file, indent=4)
        pref_file.close()

    except Exception as e:
        message = "Contact mGear's developers reporting this issue to get help"
        print("{} - {} / {}".format(type(e).__name__, e,
                                    message))
        return None


def unload_rig(rig_node, method):
    """ Hides or unloads the given rig

    Args:
        rig_node (str): The rig root node name
        method (int): 0=hide, 1=unload
    """

    if method and cmds.referenceQuery(rig_node, rfn=True):
        cmds.file(fr=cmds.referenceQuery(rig_node, rfn=True))
    else:
        cmds.setAttr("{}.lodVisibility".format(rig_node), False)


def wrap_maya_window():
    """ Returns a qt widget warp of the Maya window

    Returns:
        PySide2.QtWidgets or None: Maya window on a qt widget.
                                   Returns None if Maya is on batch
    """

    if __is_maya_batch():
        return None

    # gets Maya main window object
    maya_window = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(maya_window), QtWidgets.QMainWindow)
