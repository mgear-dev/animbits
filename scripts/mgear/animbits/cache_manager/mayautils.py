
# imports
from __future__ import absolute_import
import os
import json
from mgear.animbits.cache_manager.query import _MANAGER_PREFERENCE_PATH
from mgear.animbits.cache_manager.query import _MANAGER_PREFERENCE_FILE


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


def __create_preference_file():
    """ Creates the json file to store preferences for the cache manager

    The preference file is created inside the preference folder. It's placement
    is defined by the MAYA_APP_DIR environment variable and it's name by the
    _MANAGER_PREFERENCE_FILE constant

    :return: Path to the preference file
    :rtype: str
    """

    try:
        # creates file
        pref_file = open("{}/{}".format(_MANAGER_PREFERENCE_PATH,
                                        _MANAGER_PREFERENCE_FILE), "w")

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


def create_cache_manager_preference_file():
    """ Creates the Animbits cache manager preference file

    :return: Path to the preference file if existing or created one.
             None if failed
    :rtype: str or None
    """

    pref_file = "{}/{}".format(_MANAGER_PREFERENCE_PATH,
                               _MANAGER_PREFERENCE_FILE)

    if not os.path.exists(pref_file):
        __create_preference_folder()
        pref_file = __create_preference_file()

    return pref_file
