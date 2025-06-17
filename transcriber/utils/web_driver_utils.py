from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.by import By
import time
from transcriber.utils.constants.paths import Paths
from transcriber.utils.web_driver_config import config

class WebdriverUtils:
    """Utilitiy to help create Selenium webdriver instances"""
    @classmethod
    def get_driver_settings(cls, id : str):
        """Retrieve driver settings from web_driver_config file"""
        settings = cls._verify_settings(id)

        return cls._build_options(settings)
    
    @classmethod
    def _build_options(cls, settings : dict):
        """Return ChromeOptions instance with the provided settings"""
        driver_options = webdriver.ChromeOptions()
        # driver_options.add_argument("")
        for setting_key in settings:
            try:
                driver_options.add_argument(settings[setting_key])
            except InvalidArgumentException:
                pass
        return driver_options

    @classmethod
    def _verify_settings(cls, id : str): 
        """Update settings if they do not exist"""
        settings = config.read(id)
        if settings["id"] == "default":
            settings["id"] = id
            # Adjust window size to circumvent issue where element visibility is affected by
            # screen size
            settings["driver_settings"]["window_size"] = cls._calculate_window_size()
       
            
            config.write(id, settings)
        
        return settings["driver_settings"]
    
    @classmethod
    def _calculate_window_size(cls):
        """Adjust window size until element can be found
        NOTE: this is used to handle an issue where elements are hidden due to 
        a device's native screen size
        """
        width = 945
        height = 1018
        driver = webdriver.Chrome()
        while width >= 800:
            driver.set_window_size(width, height)
            try:
                driver.get("https://www.youtube.com/watch?v=GhTAoilsFUs&t=7s")
                time.sleep(5)
                driver.find_element(By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION).click()
                time.sleep(5)
                break
            except:
                width -= 50

        driver.quit() 
        return f"window-size={width},{height}"
