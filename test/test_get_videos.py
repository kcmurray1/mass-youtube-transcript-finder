import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from transcript_finder.transcriber.transcript import TranscriptProcessor
from transcript_finder.transcriber.utils.constants.paths import Paths
"""OUTDATED.."""
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



@pytest.fixture(autouse=True)
def reset_driver_state(driver):
    # This runs before every test automatically
    driver.delete_all_cookies()


# NOTE: Previous test may interfere with the upcoming tests. Appears to be
# An issue related to Selenium webdriver changing focus between windows?
def test_render_videos_from_video_count(test_channel, transcriber : TranscriptProcessor):

    channel, driver = test_channel

    driver.get(channel.url)

    transcriber._render_videos(int(driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT).text.split()[0]))

    
    videos = driver.find_elements(By.ID, Paths.ID_VIDEO) 

    assert len(videos) == channel.video_count


def test_transcriber_find_videos_from_channel_url(test_channel, transcriber : TranscriptProcessor):
    channel, driver = test_channel

    videos = transcriber.find_videos(channel.url, driver=driver)
    
    assert len(videos) == channel.video_count


def test_transcriber_find_videos_from_playlist_url(test_channel, transcriber : TranscriptProcessor):
    channel, driver = test_channel
    videos = transcriber.find_videos(channel.playlist_url, driver=driver)

    assert len(videos) == channel.playlist_video_count

def test_transcriber_find_videos_invalid_url(test_channel, transcriber : TranscriptProcessor):
    _, driver = test_channel

    videos = transcriber.find_videos('', driver=driver)

    assert len(videos) == 0
