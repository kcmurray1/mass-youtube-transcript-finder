from rest_framework import generics
from transcript_finder_app.models import Video, Channel, Transcript
from transcript_finder_app.serializers import ChannelSerializer, ChannelVideosSerializer
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

import os
from dotenv import load_dotenv
import requests
from selenium import webdriver
from mysql.connector import pooling

from transcriber.screaper_threaded import ScraperThreaded
from transcriber.logger import DBLogger
from transcriber.scraper import Scraper

from django.db import connection
from rest_framework.request import Request
from django.shortcuts import redirect
class TranscriptSearchAPI(APIView):
    def get(self, request : Request):
        try:
            search_term = request.GET.get('term')
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT v.title, v.url
                    FROM transcript_finder_app_transcript t
                    JOIN transcript_finder_app_video v
                    ON t.video_id = v.id          
                    AND MATCH(t.transcript) AGAINST (%s IN NATURAL LANGUAGE MODE)
                    LIMIT 50
                """, [search_term])
                rows = cursor.fetchall()
                request.session['result'] = rows
            return redirect('/search/')
            # return Response({'result': rows})
        
        except Exception as e:
            return Response({'error' : f'Internal Server Error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def search_channel(self, channel_name):
       
        url = f'https://www.youtube.com/@{channel_name}/streams'
        
        
        main_driver = webdriver.Chrome()
        videos = Scraper.find_videos(url, author=channel_name, driver=main_driver)
    
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



class ChannelCollection(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.query_params.get('include_videos') == 'true':
            return ChannelVideosSerializer
        return ChannelSerializer

    def get_queryset(self):
        queryset = Channel.objects.annotate(video_count=Count('videos'))
        return queryset

class ChannelRecord(generics.RetrieveUpdateDestroyAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

