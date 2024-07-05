from transcriber.transcript import TranscriptProcessor
from tests.test_resources import test_valid_data, InvalidData, TestResult
from selenium import webdriver
import unittest


class TestYtVideo(unittest.TestCase):

    def test_a(self):
        pass

class TestTranscriber(unittest.TestCase):
    test_transcriber = TranscriptProcessor()
    test_results = dict()
    test_web_driver = webdriver.Chrome()

    def test_a_non_youtube_url_video_retrieval_count(self):
        self.test_results[InvalidData.INVALID_GOOGLE_URL.channel] = TestResult()
        retrieved_videos = self.test_transcriber.find_videos(InvalidData.INVALID_GOOGLE_URL.url)
        self.assertEquals(retrieved_videos, [])


    def test_b_youtube_url_video_retrieval_count(self):
        for test_datum in test_valid_data:
            self.test_results[test_datum.channel] = TestResult()
            retrieved_videos = self.test_transcriber.find_videos(test_datum.url)
            self.assertEquals(test_datum.vids, len(retrieved_videos))
            self.test_results[test_datum.channel].videos = retrieved_videos

    def test_c_find_matches_no_transcript_video(self):
        self.test_web_driver.get(InvalidData.INVALID_NO_TRANSCRIPT.url)
        self.test_web_driver.set_window_size(1200, 1000)

        res = self.test_transcriber._get_transcript_matches(self.test_web_driver, InvalidData.INVALID_NO_TRANSCRIPT.phrase)

        self.assertEquals(res, "timeout")
    
    # def test_d_find_phrase_match_count(self):
    #     for test_datum in test_valid_data:
    #         test_videos = self.test_results[test_datum.channel].videos
    #         num_test_matches, num_errors = self.test_transcriber.channel_search(test_videos, author=test_datum.channel, phrase=test_datum.phrase)
    #         self.assertAlmostEquals(test_datum.match_count, num_test_matches, delta=3)



def start_tests():
    # Store multiple test classes(If necessary)
    test_classes = [TestTranscriber, TestYtVideo]
    test_loader = unittest.TestLoader()
    suites = [test_loader.loadTestsFromTestCase(test_class) for test_class in test_classes]
    suites = unittest.TestSuite(suites)

    # run all tests
    unittest.TextTestRunner(verbosity=2).run(suites)

if __name__ == '__main__':
    unittest.main()