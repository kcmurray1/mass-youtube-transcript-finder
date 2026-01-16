import pytest
import mysql.connector
import os
from selenium import webdriver
from dotenv import load_dotenv
from transcript_finder.transcriber.logger import LocalLogger, DBLogger
"""Tested 11/04/2025"""
# def test_local_logger():
#     l = LocalLogger('test_file.txt', 'test_err_file.txt', 'test')

#     l.log("Hello world")
#     l.log_err("this is an error")

# def test_db_logger():
#     load_dotenv()
#     conn = mysql.connector.connect(
#         database=os.getenv('DEV_DB'),
#         user=os.getenv('USER'),
#         password=os.getenv('MYSQL_PASSWORD'),
#         host='localhost'
#     )
#     cursor = conn.cursor()

#     cursor.execute("SHOW TABLES")

#     print(cursor.fetchall())
#     conn.close()



from transcript_finder.transcriber.scraper import Scraper
from transcript_finder.transcriber.dynamic_page import DynamicPage
from mysql.connector import pooling
def test_log_from_scraper():
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("mute-audio")
    driver_options.add_argument("--windows-size=1920,1080")    
    # Use the exact UA from your fetch log
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    driver_options.add_argument(f"user-agent={ua}")

    # Add these to match the 'sec-ch' headers in the fetch
    driver_options.add_argument("--lang=en-US")
    driver_options.add_argument("--headless=new")
    # driver = webdriver.Remote(command_executor=f"http://{hub_addr}:4444/wd/hub", options=driver_options)
    driver = webdriver.Chrome(options=driver_options)

    url = ''
    driver.get(url)
    import random
    driver.execute_script("window.scrollTo(0, 400);") # Scroll to description
    time.sleep(random.uniform(2, 4))
    driver.execute_script("window.scrollTo(0, 0);")
    
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from transcript_finder.transcriber.utils.constants.paths import Paths
    import time
    WAIT_TIME_TRANSCRIPT_LOAD = 20
    WAIT_TIME_BUTTON_LOAD = 10
    transcript_lines = None
    try:
        # Wait until description element is visible
        button_description = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
        EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION))         
        )
        button_description.click()
        time.sleep(4)
        # Wait until transcript button is visible
        button_transcript = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
            EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_TRANSCRIPT))
        )
        button_transcript.click()

        # Wait for transcript content elements to load
        transcript_lines = WebDriverWait(driver, WAIT_TIME_TRANSCRIPT_LOAD).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, Paths.CSS_TEXT_TRANSCRIPT))
        )
        



    except Exception as e:
        print(str(e))
        transcript_lines = e
    finally:
        driver.quit()

    assert not isinstance(transcript_lines, Exception)

    print(transcript_lines)
    

