import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from transcriber.transcript import TranscriptProcessor
from transcriber.utils.constants.paths import Paths

class YtChannel:
    def __init__(self, channel_url, num_videos, latest_video):
        self.url = channel_url
        self.video_count = num_videos
        self.last_video = latest_video

@pytest.fixture(scope='session')
def driver():
    test_driver = webdriver.Chrome()
    yield test_driver

    test_driver.quit()

@pytest.fixture
def test_channel(driver):
    
    yield YtChannel(
        channel_url='https://www.youtube.com/@Flarvain/videos',
        num_videos=45,
        latest_video='Devlog #2 - Making Major Systems for my DREAM game 8 minutes, 45 seconds'
    ), driver

@pytest.fixture
def transcriber():
    yield TranscriptProcessor()

@pytest.fixture(autouse=True)
def reset_driver_state(driver):
    # This runs before every test automatically
    driver.delete_all_cookies()



def test_get_video_count_element(test_channel):
    channel, driver = test_channel

    driver.get(channel.url)
    vid_count = int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0])
    assert channel.video_count == vid_count


def test_get_video_element(test_channel):
    channel, driver = test_channel

    driver.get(channel.url)
    
    video = driver.find_element(By.ID, Paths.ID_VIDEO) 

    assert video.get_attribute('aria-label') == channel.last_video




def test_render_videos_from_video_count(test_channel, transcriber : TranscriptProcessor):

    channel, driver = test_channel

    driver.get(channel.url)

    transcriber._render_videos(int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0]))

    
    videos = driver.find_elements(By.ID, Paths.ID_VIDEO) 

    assert len(videos) == channel.video_count
    