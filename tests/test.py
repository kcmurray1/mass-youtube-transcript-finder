from transcriber.transcript import TranscriptProcessor
from tests.test_resources import test_data, TestResult
import unittest

class TestTranscriber(unittest.TestCase):
    test_transcriber = TranscriptProcessor()
    test_results = dict()

    def test_a_video_retrieval_count(self):
        for test_datum in test_data:
            self.test_results[test_datum.channel] = TestResult()
            retrieved_videos = self.test_transcriber.find_videos(test_datum.url)
            self.assertEquals(test_datum.vids, len(retrieved_videos))
            self.test_results[test_datum.channel].videos = retrieved_videos
    
    def test_b_find_phrase_match_count(self):
        for test_datum in test_data:
            test_videos = self.test_results[test_datum.channel].videos
            num_test_matches, num_errors = self.test_transcriber.channel_search(test_videos, author=test_datum.channel, phrase=test_datum.phrase)
            self.assertAlmostEquals(test_datum.match_count, num_test_matches, delta=3)



def start_tests():
    # Store multiple test classes(If necessary)
    test_classes = [TestTranscriber]
    test_loader = unittest.TestLoader()
    suites = [test_loader.loadTestsFromTestCase(test_class) for test_class in test_classes]
    suites = unittest.TestSuite(suites)

    # run all tests
    unittest.TextTestRunner(verbosity=2).run(suites)

if __name__ == '__main__':
    unittest.main()