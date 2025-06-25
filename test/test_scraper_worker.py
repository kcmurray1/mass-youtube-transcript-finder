import pytest
from selenium import webdriver
from transcriber.scraperworker import ScraperWorker
from transcriber.logger import Logger

@pytest.fixture(scope='session')
def driver():
    test_driver = webdriver.Chrome()
    yield test_driver

    test_driver.quit()

@pytest.fixture(autouse=True)
def reset_driver_state(driver):
    # This runs before every test automatically
    driver.delete_all_cookies()

def test_work():
    l = Logger(filepath='goob.txt', error_filepath='goob_error.txt', dir='test')

    worker = ScraperWorker(id=1, logger=l)
    url = 'https://www.youtube.com/watch?v=Pi3bI-YghF0'
    worker.work("jdh", "hello", video_url=url)

