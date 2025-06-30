import pytest
from transcriber.transcript import TranscriptProcessor

from transcriber.logger import LocalLogger
from functools import partial

from transcriber.screaper_threaded import ScraperThreaded

# @pytest.fixture(scope='session')
# def transcriber():
#     yield TranscriptProcessor()

# def test_run_with_four_workers(transcriber : TranscriptProcessor):
#     # find videos

#     # search videos
#     homepage_url = 'https://www.youtube.com/@jdh/videos'
#     playlist_url = 'https://www.youtube.com/watch?v=Z9L7u-602qQ&list=PLXVfT_0eTq66k_xLrdBWuZvDe8_UAyK0R'
#     transcriber.channel_search(author='jdh', url=homepage_url, num_workers=4, phrase="hello")


from selenium import webdriver
from transcriber.scraper import Scraper

def test_new_implementation():
        def dummy(transcript, phrase):    
            return "\n".join([match for line in transcript if (match := line.get_dom_attribute("aria-label")) and phrase in match.lower()])

        url = ''
        
        main_driver = webdriver.Chrome()
        videos = Scraper.find_videos(url, author='', driver=main_driver)
        main_driver.quit()
        videos = videos[:500]
        
        dummy_with_phrase = partial(dummy, phrase="")
        num_workers = 4

        l = LocalLogger(filepath='matches.txt', error_filepath='error_log.txt',dir='test')

        ScraperThreaded.get_transcripts(videos=videos, author='', log=l, transcript_op=dummy_with_phrase, num_workers=num_workers)
      