from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


REGEX_DATE_STR = r'\w{3} \d+, \d{4}'

class StaticPage:
    """Class of methods that perform logic based on static html of webpage"""
    def get_channel_info(user_entered_owner, driver):
        "Compare name with the official name found on the homepage"
        upload_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'page-header')))


        x = upload_info.find_element(By.TAG_NAME, "yt-content-metadata-view-model")
        x = x.text.split('\n')
        owner = x[0].lower().lstrip('@')
        vids = x[-1].split(' ')[0]

        print('found', owner, 'videos', len(vids))
        if user_entered_owner in owner:
            return owner, int(vids)
        return None, None
    
