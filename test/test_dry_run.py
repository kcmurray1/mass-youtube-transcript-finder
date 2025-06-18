import pytest
from transcriber.transcript import TranscriptProcessor


@pytest.fixture(scope='session')
def transcriber():
    yield TranscriptProcessor()

def test_run_with_four_workers(transcriber : TranscriptProcessor):
    # find videos

    # search videos
    transcriber.channel_search(author='idk', url='', num_workers=4, phrase="hello")