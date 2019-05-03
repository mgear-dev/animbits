
# imports
from __future__ import absolute_import
import os
import json
from maya import cmds
from mgear.animbits.cache_manager.query import _MANAGER_PREFERENCE_PATH
from mgear.animbits.cache_manager.query import get_preference_file
from mgear.animbits.cache_manager.query import get_cache_destination_path


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


def __check_gpu_plugin():
    """ Check for the gpuCache plugin load
    """

    if not cmds.pluginInfo('gpuCache', query=True, loaded=True):
        cmds.loadPlugin('gpuCache')


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


def generate_gpu_cache(geo_node, cache_name, start, end):
    """
    """

    cache_destination = get_cache_destination_path()

    # Runs the GPU cache generation
    gpu_file = cmds.gpuCache("{}".format(geo_node),
                             startTime=start,
                             endTime=end,
                             optimize=True,
                             optimizationThreshold=4000,
                             writeMaterials=True,
                             directory=cache_destination,
                             fileName=cache_name)

    return gpu_file


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
