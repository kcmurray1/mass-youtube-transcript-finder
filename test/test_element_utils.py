import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transcriber.transcript import TranscriptProcessor
from transcriber.utils.constants.paths import Paths
from transcriber.youtube_element_utils import YtElementUtils

class Channel:
    def __init__(self, owner, channel_url, video_count):
        self.owner = owner
        self.channel_url = channel_url
        self.video_count = video_count

class Video:
    def __init__(self, title, upload_date, owner, url):
        self.title = title
        self.upload_date = upload_date
        self.owner = owner
        self.url = url
        

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

@pytest.fixture
def TestResources():
    yield Channel(
        owner='jdh',
        channel_url=HOME_URL,
        video_count=33),Video(
        title='Multiplayer [2023] - Server Authoritative Movement - Netcode For GameObjects Pt 4',
        upload_date='2023-03-03',
        owner='flarvain',
        url='https://www.youtube.com/watch?v=XhluFjFAo4E'
    )

def test_get_elements_from_homepage(transcriber, TestResources):
    channel, _ = TestResources
    transcriber.current_author = channel.owner
    transcriber.driver.get(channel.channel_url)
    owner, vids = YtElementUtils.get_channel_info(channel.owner, driver=transcriber.driver)
    
    assert owner is not None
    assert isinstance(vids, int)

def test_get_elements_from_video(transcriber, TestResources):
    _, video = TestResources
    transcriber.driver.get(video.url)
    
    url, title, date, owner = YtElementUtils.get_video_information(transcriber.driver)

    assert video.title == title
    assert video.upload_date == str(date.date())
    assert video.owner == owner.lower()
