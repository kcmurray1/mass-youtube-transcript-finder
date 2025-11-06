from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re

REGEX_DATE_STR = r'\w{3} \d+, \d{4}'

REGEX_VIDEO_COUNT_STR = r'\d+.\d+'

class StaticPage:
    """Class of methods that perform logic based on static html of webpage"""
    def _handle_video_count(video_string):
        """Convert videos to an integer
        Ex) 1.4k videos will be converted to 1400
        """
        vids = None
        try:
            vids = int(video_string)
        except ValueError as e:
            vids = re.search(REGEX_VIDEO_COUNT_STR, video_string)
            thousands, hundreds = vids.group().split('.')
            vids = (int(thousands) * 1000) + (int(hundreds) * 100)
        return vids

    def get_channel_info(user_entered_owner, driver):
        "Compare name with the official name found on the homepage"
        upload_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'page-header')))


        x = upload_info.find_element(By.TAG_NAME, "yt-content-metadata-view-model")
        x = x.text.split('\n')
        owner = x[0].lower().lstrip('@')
        vids = StaticPage._handle_video_count(x[-1].split(' ')[0])

      
        print('found', owner, 'videos', vids)
        if user_entered_owner.lower() in owner:
            return owner, vids
        return None, None
    
