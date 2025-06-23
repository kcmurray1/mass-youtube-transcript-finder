from transcriber.utils.constants.paths import Paths
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

    
import re
from datetime import datetime
REGEX_DATE_STR = r'\w{3} \d+, \d{4}'


class YtElementUtils:
    def get_channel_info(user_entered_owner, driver):
        "Compare name with the official name found on the homepage"
        upload_info = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'page-header')))


        x = upload_info.find_element(By.TAG_NAME, "yt-content-metadata-view-model")
        x = x.text.split('\n')
        owner = x[0].lower().lstrip('@')
        vids = x[-1].split(' ')[0]

        if user_entered_owner in owner:
            return owner, int(vids)
        return None, None
    

    def get_video_information(driver : webdriver):
 
        upload_info = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'owner')))


        url = upload_info.find_element(By.TAG_NAME, "a").get_attribute("href")

        button_description = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION))         
            )
        button_description.click()


        upload_date = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'info-container'))).text

        title = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, 'title'))).text

     
        date = re.search(REGEX_DATE_STR, upload_date.strip())

        date = datetime.strptime(date.group(),"%b %d, %Y")

        uploader = upload_info.text.split('\n')[0]

        print(url, title, date, uploader)


    
    # def load_info_from_homepage(self, driver : webdriver, channel_element):
    #     x = channel_element.find_element(By.TAG_NAME, "yt-content-metadata-view-model")
    #     x = x.text.split('\n')
    #     owner = x[0]
    #     vids = x[-1].split(' ')[0]
    #     # Get the channel name
    #     channel = owner.lstrip('@')
    #     # Render all of the videos 
    #     # NOTE: old way to find video element int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0])
    #     # No issues with it, but this information is included when retreiving the channel name
    #     self._render_videos(int(vids))

    #     # NOTE: homepage videos can all be found using ID 'video-title-link' 01/02/24
    #     videos = driver.find_elements(By.ID, Paths.ID_VIDEO) 

    #     return videos, owner

    
