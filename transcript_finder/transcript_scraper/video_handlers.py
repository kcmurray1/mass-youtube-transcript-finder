"""What to do when a video is opened"""
from transcript_scraper.YTScraper import YTScraper
from transcript_finder_app.models import Video, Channel, Transcript
from selenium import webdriver
def test(driver : webdriver.Chrome, video_url, transcript_op):
    # return if video_url exists and has a transcript
    if Video.objects.filter(url=video_url, transcript__isnull=False).exists():
        return 
    # continue if no transcript or no video_url in database 
    driver.get(video_url)

    title, date, channel_name = YTScraper.get_video_information(driver)
    
    # get transcript from url  
    driver.refresh()
    transcript_text = YTScraper.get_transcript(driver)

    # save channel if not already in DB     
    channel_obj, _ = Channel.objects.get_or_create(name=channel_name)
    # save video to db if not already in DB, otherwise update video to have an associated transcript
    video_obj, _ = Video.objects.update_or_create(
        url=video_url,
        defaults={
            'title': title,
            'date': date,
            'channel': channel_obj
         }
    )

    # save transcript to database(this is the main reason why this logic reached this point)
    if isinstance(transcript_text, Exception):
        return
    transcript_obj, _ = Transcript.objects.update_or_create(
        video=video_obj,
        defaults={
            'transcript': transcript_op(transcript_text)
        }
    )

def test_transcript(driver, video_url, transcript_op):
    print('1124')
    driver.get(video_url)


    transcript_text = YTScraper.get_transcript(driver)

    print(transcript_text)