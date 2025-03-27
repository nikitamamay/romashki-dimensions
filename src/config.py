from src import config_reader


PROGRAM_NAME = "RomashkiDimensions"
APP_CONFIG_FOLDER = config_reader.get_user_config_folder(PROGRAM_NAME)



cr = config_reader.ConfigReader.load_or_create_default_config_in_configfolder(
    APP_CONFIG_FOLDER,
    {
        # see default options below in CONFIG CHECK section
    }
)
cr._verbose_saving = True

save = cr.save
options = cr._cfg

print(options)


### CONFIG CHECK

def check():
    try:
        assert isinstance(cr._cfg["window_stays_on_top"], bool)
    except:
        cr._cfg["window_stays_on_top"] = True

    try:
        assert isinstance(cr._cfg["icon_size"], int)
    except:
        cr._cfg["icon_size"] = 24

    try:
        assert isinstance(cr._cfg["is_angle_DMS"], bool)
    except:
        cr._cfg["is_angle_DMS"] = True

    try:
        assert isinstance(cr._cfg["remember_window_geometry"], bool)
    except:
        cr._cfg["remember_window_geometry"] = False

    try:
        assert isinstance(cr._cfg["window_geometry"], list)
        assert len(cr._cfg["window_geometry"]) == 4
        for el in cr._cfg["window_geometry"]:
            assert isinstance(el, int) and el > 0
    except:
        cr._cfg["window_geometry"] = [0, 0, 0, 0]

check()

