import json

CONFIG_FILE_PATH = "nodes/utils/config.json"

def get_config():
     with open(CONFIG_FILE_PATH, "r") as f:
        return json.load(f)

def get_driver_settings(id : str):
    """Getting webdriver information for specific device by id lookup"""
    with open(CONFIG_FILE_PATH, "r") as f:
        data = json.load(f)
    # check if id exists
        try:
            return data[id]
        except KeyError:
            return data["default"]


def update_driver_settings(id: str, data : dict):
    """update config file at device id"""
    if not data or not isinstance(data, dict):
      raise Exception(f"Invalid Data: {data}")
    
    # update config data with new data for id
    config_data = get_config()
    config_data[id] = data

    with open(CONFIG_FILE_PATH, "w") as f:
        json.dump(config_data, f, indent=4)



