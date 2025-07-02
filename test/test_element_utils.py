import pytest
from selenium import webdriver
from transcriber.scraper import Scraper

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

@pytest.fixture(autouse=True)
def reset_driver_state(driver):
    # This runs before every test automatically
    driver.delete_all_cookies()

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

def test_get_elements_from_homepage(TestResources, driver):
    channel, _ = TestResources

    driver.get(channel.channel_url)
    owner, vids = Scraper.get_channel_info(channel.owner, driver)
    
    assert owner is not None
    assert isinstance(vids, int)

def test_get_elements_from_video(TestResources, driver):
    _, video = TestResources
    driver.get(video.url)
    
    url, title, date, owner = Scraper.get_video_information(driver)

    assert video.title == title
    assert video.upload_date == str(date.date())
    assert video.owner == owner.lower()
