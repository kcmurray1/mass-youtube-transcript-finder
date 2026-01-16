from selenium import webdriver
import requests
import multiprocessing

from transcript_finder.transcriber.scraper import Scraper
from dotenv import load_dotenv
from mysql.connector import pooling
from transcript_finder.transcriber.screaper_threaded import ScraperThreaded
from transcript_finder.transcriber.logger import LocalLogger, DBLogger
import os
import time


def debug_transcript():
  

    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("mute-audio")
    driver_options.add_argument("--windows-size=1920,1080")    
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    driver_options.add_argument(f"user-agent={ua}")
    driver_options.add_argument("--disable-blink-features=AutomationControlled")
    driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver_options.add_experimental_option('useAutomationExtension', False)

    # Add these to match the 'sec-ch' headers in the fetch
    driver_options.add_argument("--lang=en-US")
    driver_options.add_argument("--headless=new")
    driver = webdriver.Remote(command_executor=f"http://{hub_addr}:4444", options=driver_options)
    # driver = webdriver.Chrome(options=driver_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """
    })

    url = 'https://www.youtube.com/watch?v=Zyw78NvHdRQ'
    driver.get(url)
    
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from transcript_finder.transcriber.utils.constants.paths import Paths
    WAIT_TIME_TRANSCRIPT_LOAD = 10
    WAIT_TIME_BUTTON_LOAD = 10
    transcript_lines = None
    try:
        # Wait until description element is visible
        button_description = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
        EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION))         
        )
        button_description.click()
        # Wait until transcript button is visible
        button_transcript = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
            EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_TRANSCRIPT))
        )
        button_transcript.click()
        # Wait for transcript content elements to load
        transcript_lines = WebDriverWait(driver, WAIT_TIME_TRANSCRIPT_LOAD).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, Paths.CSS_TEXT_TRANSCRIPT))
        )
        
        transcript_lines = [line.get_dom_attribute("aria-label") for line in transcript_lines]
   
    except Exception as e:
        transcript_lines = e
    finally:
        driver.quit()

    if isinstance(transcript_lines, Exception):
        print('err',str(transcript_lines))
    else:
        print(transcript_lines)
    


def test_with_db_logger(videos, num_workers, addr):
    #url = ''
     

    # main_driver = webdriver.Chrome()
    # videos = Scraper.find_videos(url, author='', driver=main_driver)
    
    print(videos)
    
    # main_driver.quit()

   
    # print(multiprocessing.current_process().pid, videos, len(videos))

    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])

  
    load_dotenv()
    dbconfig = {
        'database' : os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host' : os.getenv('DB_HOST', 'localhost')
    }
    conn_pool = pooling.MySQLConnectionPool(
        pool_size=32,
        pool_name="worker_pool",
        **dbconfig

    )
    db = DBLogger(conn_pool)
    ScraperThreaded.get_transcripts(videos=videos, author='', log=db, transcript_op=default_transcript, num_workers=num_workers, hub_addr=addr)

    # print(multiprocessing.current_process().pid, 'done')

def get_vids(url):
    main_driver = webdriver.Chrome()
    videos = Scraper.find_videos(url, author='MercyModiste', driver=main_driver)
    
    
    
    main_driver.quit()

    return videos

if __name__ == "__main__":
    debug_transcript()

    import os

   
    # test_with_db_logger(VIDEOSV2, 9, hub_addr)

    # print(len(all_videos))

    # test_with_db_logger(all_videos, 20, '')
 