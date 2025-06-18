import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transcriber.transcript import TranscriptProcessor
from transcriber.utils.constants.paths import Paths
from transcriber.yt_video import YtVideo

@pytest.fixture(scope='session')
def transcriber():
    yield TranscriptProcessor()

@pytest.fixture(scope='session')
def driver():
    test_driver = webdriver.Chrome()
    yield test_driver

    test_driver.quit()

def test_convert_html_element_to_yt_video(driver):
    channel_url = 'https://www.youtube.com/@Flarvain/videos'

    # Get video
    driver.get(channel_url)
    video = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, Paths.ID_VIDEO)))

    print(YtVideo(video.get_dom_attribute("aria-label"), video.get_attribute("href")).as_json())





    