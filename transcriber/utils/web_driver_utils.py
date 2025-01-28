from selenium import webdriver
from transcriber.utils.web_driver_config import config
class WebdriverUtils:
    
    def get_driver_settings(self, id : str):
        return self._verify_settings(id)
    
    def _verify_settings(self, id : str): 
        """Update settings if they do not exist"""
        settings = config.get_value(id)
        if settings["id"] == "default":
            settings["id"] = id
            # Adjust window size to circumvent issue where elements
            # are unclickable
            
            config.update_driver_settings(id, settings)
        return settings["driver_settings"]

    def _calculate_window_size():
        return f"window-size{2}"
