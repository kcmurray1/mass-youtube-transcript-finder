import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transcriber.transcript import TranscriptProcessor
from transcriber.utils.constants.paths import Paths
from transcriber.youtube_element_utils import YtElementUtils


HOME_URL = 'https://www.youtube.com/@jdh/videos'
PLAYLIST_URL = 'https://www.youtube.com/watch?v=Z9L7u-602qQ&list=PLXVfT_0eTq66k_xLrdBWuZvDe8_UAyK0R'

@pytest.fixture(scope='session')
def driver():
    test_driver = webdriver.Chrome()
    yield test_driver

    test_driver.quit()


@pytest.fixture(scope='session')
def transcriber(driver):
    yield TranscriptProcessor(driver=driver)

@pytest.fixture(autouse=True)
def reset_driver_state(transcriber : TranscriptProcessor):
    # This runs before every test automatically
    transcriber.driver.delete_all_cookies()

def test_get_elements_from_homepage(transcriber):
    transcriber.current_author = 'jdh'
    transcriber.driver.get(HOME_URL)
    owner, vids = YtElementUtils.get_channel_info("jdh", driver=transcriber.driver)
    
    assert owner is not None
    assert isinstance(vids, int)

def test_get_elements_from_video(transcriber):
    video_url = 'https://www.youtube.com/watch?v=XhluFjFAo4E'
    transcriber.driver.get(video_url)
    
    YtElementUtils.get_video_information(transcriber.driver)