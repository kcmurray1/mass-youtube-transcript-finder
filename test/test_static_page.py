import pytest
from selenium import webdriver
from transcript_finder.transcriber.static_page import StaticPage
"""Last tested 11/4/25"""
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
    basic = Channel(
        owner='jdh',
        channel_url=HOME_URL,
        video_count=33)
    thousand_videos = Channel(
        owner='',
        channel_url='',
        video_count=1400
    )
    yield {"basic" : basic, "thousands": thousand_videos}

def test_get_elements_from_homepage(TestResources, driver):
    channel = TestResources['basic']
    driver.get(channel.channel_url)
    owner, vids = StaticPage.get_channel_info(channel.owner, driver)
    
    assert owner is not None
    assert owner == channel.owner
    assert isinstance(vids, int)
    assert vids == channel.video_count

def test_get_thousand_video_format(TestResources, driver):
    channel = TestResources['thousands']
    driver.get(channel.channel_url)
    owner, vids = StaticPage.get_channel_info(channel.owner, driver)
    
    assert owner is not None
    assert owner == channel.owner.lower()
    assert isinstance(vids, int)
    assert vids == channel.video_count
