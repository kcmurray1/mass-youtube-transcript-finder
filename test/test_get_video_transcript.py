import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transcriber.transcript import TranscriptProcessor
from transcriber.utils.constants.paths import Paths

PAGELOADTIME = 10
WAIT_TIME_TRANSCRIPT_LOAD = 20
WAIT_TIME_BUTTON_LOAD = 10


class TranscriptQuery:
    def __init__(self, url, search_item):
        self.video_url = url
        self.search_term = search_item

@pytest.fixture(scope='session')
def driver():
    test_driver = webdriver.Chrome()
    yield test_driver

    test_driver.quit()

@pytest.fixture
def test_video(driver):
    
    video_url = 'https://www.youtube.com/watch?v=u8wrPlpeO5A&t=9s'

    yield TranscriptQuery(video_url, "interesting"), driver

@pytest.fixture(scope='session')
def transcriber(driver):
    yield TranscriptProcessor(driver=driver)

@pytest.fixture(autouse=True)
def reset_driver_state(driver):
    # This runs before every test automatically
    driver.delete_all_cookies()

def test_get_transcript_elements(test_video):

    query, driver = test_video

    driver.get(query.video_url)

    # Wait until description element is visible
    button_description = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
        EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION))         
    )
    assert button_description is not None

    button_description.click()

    button_transcript = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
        EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_TRANSCRIPT))
    )

    assert button_transcript is not None
    
    button_transcript.click()
    # Wait for transcript content elements to load
    transcript_lines = WebDriverWait(driver, WAIT_TIME_TRANSCRIPT_LOAD).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, Paths.CSS_TEXT_TRANSCRIPT))
    )

    assert transcript_lines is not None
    
def test_find_phrase_in_transcript_element(test_video, transcriber : TranscriptProcessor):
    query, driver = test_video

    driver.get(query.video_url)
    results = transcriber._get_transcript_matches(driver, query.search_term)

    assert len(results) == 3
    