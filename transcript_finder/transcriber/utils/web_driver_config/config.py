import json
CONFIG_FILE_PATH = "transcriber/utils/web_driver_config/config.json"

def get_config() -> dict:
     with open(CONFIG_FILE_PATH, "r") as f:
        return json.load(f)

def read(id : str, key : str = None) -> any:
    """Retrieve value from ID in config
    Args:
      id: a str representing the id for a system data stored
          in the CONFIG_FILE_PATH
      key: a str for the key to retrieve from the retrieved system data
    Return:
      all data for id if no key provided
      Note: returns all data associated with default ID if invalid ID is given
      Note: returns all data associated with given ID if key is not present or invalid
    Exceptions:
      Raises ValueError if id is not a str
    """
    if not id or not isinstance(id, str):
        raise ValueError(f"Invalid ID type: {id} {type(id)}")
    
    with open(CONFIG_FILE_PATH, "r") as f:
        data = json.load(f)

        print("reading...", data)
    # check if id exists
        try:
            if not key:
                return data[id]
            return data[id][key]
        except KeyError:
            if not key:
                return data["default"]
            return data["default"][key]

def write(id: str, data : dict):
    """update config file"""
    if not data or not isinstance(data, dict):
        raise KeyError(f"Invalid Data: {data}")    
    config_data = get_config()
    try:
        # update config data with new data for id
        config_data[id] = data
        print("writing..", config_data[id])
    except KeyError:
        pass
    
 
    with open(CONFIG_FILE_PATH, "w") as f:
            json.dump(config_data, f, indent=4)


def update_driver_settings(id: str, data : dict):
    """update config file at device id"""
    if not data or not isinstance(data, dict):
      raise Exception(f"Invalid Data: {data}")
    
    # update config data with new data for id
    config_data = get_config()
    config_data[id] = data

    with open(CONFIG_FILE_PATH, "w") as f:
        json.dump(config_data, f, indent=4)



