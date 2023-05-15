from yaml import load, Loader, dump, Dumper 

def open_config():
    with open("device/camera/camera_setting.yml") as f:
        return load(f, Loader)
    
def get_config(yml, mode, entry):
    return yml[mode][entry]

def set_config(yml, mode, entry, new_val):
    yml[mode][entry] = new_val 

def save_config(yml):
    with open("camera_setting.yml", "w") as f:
        dump(yml, f, Dumper)