import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transcriber.scraper import Scraper
from transcriber.utils.constants.paths import Paths
from transcriber.youtube_element_utils import YtElementUtils



@pytest.fixture(scope='session')
def driver():
    test_driver = webdriver.Chrome()
    yield test_driver

    test_driver.quit()

@pytest.fixture(autouse=True)
def reset_driver_state(driver):
    # This runs before every test automatically
    driver.delete_all_cookies()

def test_get_videos_from_homepage(driver):
    url = 'https://www.youtube.com/@Flarvain/videos'
    channel = 'flarvain'

    videos = Scraper.find_videos(url, channel, driver)

    assert len(videos) == 45

# def test_get_videos_from_playlist(driver):

#     playlist_url='https://www.youtube.com/watch?v=eX6g46aDLos&list=PL8K0QjCk8ZmigG5vw6ZizlZDvLEaAhNo4'
#     channel = 'flarvain'

#     videos = Scraper.find_videos(playlist_url, channel, driver)

#     assert len(videos) == 13

# def test_get_transcript(driver):
#     video_url = 'https://www.youtube.com/watch?v=Pi3bI-YghF0'
    
#     driver.get(video_url)
#     transcript = Scraper.get_transcript(driver)

#     assert not isinstance(transcript, Exception)

#     output_file = 'test/debug_fil.txt'

#     with open(output_file, "a") as f:
#         for line in transcript:
#             f.write(line.get_dom_attribute('aria-label'))
     
