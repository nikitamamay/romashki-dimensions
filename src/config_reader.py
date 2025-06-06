import os
import json
import sys

from src.json_utils import JSONable


class IConfig(JSONable):
    pass


def get_user_config_folder(program_name: str) -> str:
    if sys.platform == "win32":
        folder_path = os.getenv("APPDATA")
    elif sys.platform == "linux":
        folder_path = "~/.config"
    else:
        print(f'Your current platform is "{sys.platform}". Only "win32" and "linux" is supported for now. Sorry.')
        sys.exit(1)
    return os.path.abspath(os.path.join(folder_path, program_name))


def exists(filepath: str) -> bool:
    return os.path.exists(filepath)


def is_folder_creatable(filepath: str) -> bool:
    filepath = os.path.abspath(filepath)
    drive = os.path.splitdrive(filepath)[0]
    if not os.path.exists(drive):
        return False
    while not os.path.exists(filepath):
        filepath = os.path.dirname(filepath)
    return True


def is_file_creatable(filepath: str) -> bool:
    return is_folder_creatable(os.path.dirname(os.path.abspath(filepath)))


def ensure_folder(filepath: str) -> None:
    filepath = os.path.abspath(filepath)
    if not os.path.isdir(filepath):
        os.makedirs(filepath)


def ensure_file(filepath: str) -> None:
    ensure_folder(os.path.dirname(os.path.abspath(filepath)))
    with open(filepath, "a", encoding='utf-8') as f:
        pass


def do_paths_intersect(path1: str, path2: str) -> bool:
    sp1 = str(os.path.abspath(path1))
    sp2 = str(os.path.abspath(path2))
    return sp1.startswith(sp2) or sp2.startswith(sp1)



class ConfigReader():
    def __init__(self, default_config: dict = {}) -> None:
        self._filepath: str = ""

        self._default_config: dict = default_config
        self._cfg: dict = self._default_config.copy()
        self._verbose_saving = False

    @staticmethod
    def load_or_create_default_config_in_configfolder(config_foler_path: str, default_config: dict = {}) -> 'ConfigReader':
        app_config_file = os.path.join(config_foler_path, "cfg.json")

        if os.path.exists(app_config_file):
            return ConfigReader.read_from_file(app_config_file, default_config)
        else:
            # print(app_config_folder, app_config_file, sep="\n")
            cr = ConfigReader(default_config)
            cr.set_filepath(app_config_file)
            cr.save()
            return cr

    @staticmethod
    def read_from_file(filepath: str, default_config: dict = {}) -> 'ConfigReader':
        if not os.path.isfile(filepath):
            raise Exception(f'"{filepath}" is not a file or does not exist')

        cr = ConfigReader(default_config)
        cr.set_filepath(filepath)
        cr.reload()
        return cr

    def copy(self) -> 'ConfigReader':
        cr = ConfigReader(self._default_config.copy())
        cr._cfg = self._cfg.copy()
        return cr

    def assign(self, cr: 'ConfigReader') -> None:
        self._cfg = cr._cfg.copy()
        self._default_config = cr._default_config.copy()

    def save(self, config: dict = None) -> None:
        if self._filepath == "":
            raise Exception('Config filename is not specified')

        ensure_file(self._filepath)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(
                self._cfg if config is None else config,
                f,
                ensure_ascii=False,
                indent=2
            )
        if self._verbose_saving:
            print("Config saved.")

    def save_default(self) -> None:
        self.save(self._default_config)

    def reload(self) -> dict:
        if not os.path.isfile(self._filepath):
            self.save_default()
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                self._cfg.update(json.load(f))
        except Exception as e:
            print(e.__class__.__name__, ": ", str(e), sep="")
            print("Using the default config.")

    def set_filepath(self, filepath: str) -> None:
        self._filepath = os.path.abspath(filepath)

    def get_filepath(self) -> str:
        return self._filepath

    def set_default_config(self, default_config: dict) -> None:
        self._default_config = default_config





if __name__ == "__main__":
    p1 = ""
    p2 = "../../hey/"

    print(do_paths_intersect(p1, p2))

    sys.exit()

    # testing
    PROGRAM_NAME = "PythonConfigReader"
    APP_CONFIG_FOLDER = get_user_config_folder(PROGRAM_NAME)
    APP_CONFIG_FILE = os.path.join(APP_CONFIG_FOLDER, "cfg.json")

    print(APP_CONFIG_FOLDER, APP_CONFIG_FILE, sep="\n")

    cr = ConfigReader.load_or_create_default_config_in_configfolder(PROGRAM_NAME, {
        "a": 1,
        "b": "hello",
        "c": [45, "forty-five"],
    })

    print(cr._cfg)

    cr.save()
