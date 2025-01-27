from transcriber.transcript import TranscriptProcessor
from transcriber.paths import Paths
from tests.test_resources import ValidData, InvalidData, TestResult
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import unittest
import time

class TestElementPaths(unittest.TestCase):
    """Verify that element paths are up to date"""
    @classmethod
    def setUpClass(cls):
        cls.test_element_driver = webdriver.Chrome()
        cls.test_element_driver.get(ValidData.VALID_CHANNEL_URL)

    def test_a_find_video_count(self):
        res = self.test_element_driver.find_element(By.XPATH, Paths.XPATH_VIDEO_COUNT)
        self.assertIsNotNone(res)

    def test_b_find_video_link(self):
        res = self.test_element_driver.find_elements(By.ID, Paths.ID_VIDEO)
        self.assertIsNotNone(res)

    def test_c_find_button_description(self):
        # Change to single Youtube video
        self.test_element_driver.get(ValidData.VALID_VIDEO_URL)
        time.sleep(5)

        res = self.test_element_driver.find_element(By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION)
        self.assertIsNotNone(res)
        res.click()

       
    # NOTE: this test may fail if a Youtube pop-up blocks the transcript button
    def test_d_find_button_transcript(self):
        res = self.test_element_driver.find_element(By.XPATH, Paths.XPATH_BUTTON_TRANSCRIPT)
        self.assertIsNotNone(res)
        res.click()


    def test_e_find_text(self):
        search = "dev"
        time.sleep(5)
        matches = self.test_element_driver.find_elements(By.XPATH, Paths.XPATH_TEXT_FIND_PATTERN_V2.format(search=search))

        for match in matches:
            print(match.get_dom_attribute("aria-label"))
      
        time.sleep(5)
        self.test_element_driver.quit()

    




class TestYtVideo(unittest.TestCase):
    def test_a(self):
      pass

class TestTranscriber(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_transcriber = TranscriptProcessor()
        cls.test_results = dict()
        cls.test_web_driver = webdriver.Chrome()

    def test_a_non_youtube_url_video_retrieval_count(self):
        self.test_results[InvalidData.INVALID_GOOGLE_URL.channel] = TestResult()
        retrieved_videos = self.test_transcriber.find_videos(InvalidData.INVALID_GOOGLE_URL.url)
        self.assertEqual(retrieved_videos, [])


    def test_b_youtube_url_video_retrieval_count(self):
        for test_datum in ValidData.VALID_TRANSCRIBER_TEST_DATA:
            self.test_results[test_datum.channel] = TestResult()
            retrieved_videos = self.test_transcriber.find_videos(test_datum.url)
            self.assertEqual(test_datum.vids, len(retrieved_videos))
            self.test_results[test_datum.channel].videos = retrieved_videos

    # def test_c_find_matches_no_transcript_video(self):
    #     self.test_web_driver.get(InvalidData.INVALID_NO_TRANSCRIPT.url)
    #     self.test_web_driver.set_window_size(1200, 1000)

    #     res = self.test_transcriber._get_transcript_matches(self.test_web_driver, InvalidData.INVALID_NO_TRANSCRIPT.phrase)

    #     self.assertEquals(res, "timeout")
    
    def test_d_find_phrase_match_count(self):
        for test_datum in ValidData.VALID_TRANSCRIBER_TEST_DATA:
            test_videos = self.test_results[test_datum.channel].videos
            num_test_matches, num_errors = self.test_transcriber.channel_search(test_videos, author=test_datum.channel, phrase=test_datum.phrase)
            self.assertAlmostEqual(test_datum.match_count, num_test_matches, delta=3)



def start_tests():
    # Store multiple test classes(If necessary)
    # test_classes = [TestElementPaths,TestTranscriber, TestYtVideo]
    test_classes = [TestElementPaths]
    test_loader = unittest.TestLoader()
    suites = [test_loader.loadTestsFromTestCase(test_class) for test_class in test_classes]
    suites = unittest.TestSuite(suites)

    # run all tests
    unittest.TextTestRunner(verbosity=2).run(suites)
