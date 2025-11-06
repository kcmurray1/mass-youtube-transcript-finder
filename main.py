from selenium import webdriver
import requests

from transcript_finder.transcriber.scraper import Scraper
from dotenv import load_dotenv
from mysql.connector import pooling
from transcript_finder.transcriber.screaper_threaded import ScraperThreaded
from transcript_finder.transcriber.logger import LocalLogger, DBLogger
import os
def test_with_db_logger():
    url = ''
     
    
    main_driver = webdriver.Chrome()
    videos = Scraper.find_videos(url, author='ScarleYonaguni', driver=main_driver)
  
    main_driver.quit()

    

    res = requests.get(f"http://localhost:4444/status")
    x = res.json()

    num_workers = 0

    for node in x["value"]["nodes"]:
        print(f"max sessions {node["maxSessions"]}")
        num_workers += node["maxSessions"]


    def default_transcript(transcript):
        return "\n".join([line.get_dom_attribute("aria-label") for line in transcript])

  
    load_dotenv()
    dbconfig = {
        'database' : os.getenv('DEV_DB'),
            'user': os.getenv('USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'host' :'localhost'
    }
    conn_pool = pooling.MySQLConnectionPool(
        pool_size=32,
        pool_name="worker_pool",
        **dbconfig

    )
    db = DBLogger(conn_pool)

    ScraperThreaded.get_transcripts(videos=videos, author='', log=db, transcript_op=default_transcript, num_workers=num_workers)



if __name__ == "__main__":
    test_with_db_logger()
   