import pytest
from transcriber.transcript import TranscriptProcessor


@pytest.fixture(scope='session')
def transcriber():
    yield TranscriptProcessor()

def test_run_with_four_workers(transcriber : TranscriptProcessor):
    # find videos

    # search videos
    homepage_url = 'https://www.youtube.com/@jdh/videos'
    playlist_url = 'https://www.youtube.com/watch?v=Z9L7u-602qQ&list=PLXVfT_0eTq66k_xLrdBWuZvDe8_UAyK0R'
    transcriber.channel_search(author='jdh', url=homepage_url, num_workers=4, phrase="hello")