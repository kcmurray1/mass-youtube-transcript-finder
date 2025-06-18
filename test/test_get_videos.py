import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transcriber.transcript import TranscriptProcessor
from transcriber.utils.constants.paths import Paths

class YtChannel:
    def __init__(self, channel_url, num_videos, latest_video, playlist_url, playlist_vid_count):
        self.url = channel_url
        self.video_count = num_videos
        self.last_video = latest_video
        self.playlist_url=playlist_url
        self.playlist_video_count=playlist_vid_count

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
        latest_video='Devlog #2 - Making Major Systems for my DREAM game 8 minutes, 45 seconds',
        playlist_url='https://www.youtube.com/watch?v=eX6g46aDLos&list=PL8K0QjCk8ZmigG5vw6ZizlZDvLEaAhNo4',
        playlist_vid_count=13
    ), driver

@pytest.fixture(scope='session')
def transcriber(driver):
    yield TranscriptProcessor(driver=driver)

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
    video = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, Paths.ID_VIDEO)))

    assert video.get_attribute('aria-label') == channel.last_video




def test_render_videos_from_video_count(test_channel, transcriber : TranscriptProcessor):

    channel, driver = test_channel

    driver.get(channel.url)

    transcriber._render_videos(int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0]))

    
    videos = driver.find_elements(By.ID, Paths.ID_VIDEO) 

    assert len(videos) == channel.video_count


def test_transcriber_find_videos_from_channel_url(test_channel, transcriber : TranscriptProcessor):
    channel, _ = test_channel

    videos = transcriber.find_videos(channel.url)
    
    assert len(videos) == channel.video_count


    # videos = transcriber.find_videos(channel.playlist_url)

    # assert len(videos) == channel.playlist_video_count

