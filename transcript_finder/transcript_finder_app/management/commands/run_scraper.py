from django.core.management.base import BaseCommand
import queue
import threading
from transcript_scraper.worker import ScraperWorker
from transcript_scraper.transcript_handlers import get_transcript_raw_text, get_transcript_fast
from transcript_scraper.video_handlers import test, test_transcript
from transcript_scraper.YTScraper import YTScraper
from selenium import webdriver
# from transcripter_finder_app.models import Video # Example model
# Import your Selenium logic here

VIDEOSV5 = ['https://www.youtube.com/watch?v=u9nUxSCSUII', 'https://www.youtube.com/watch?v=Y5WrSIB9jpM', 'https://www.youtube.com/watch?v=8VQ75_Wg1dA', 'https://www.youtube.com/watch?v=Zyw78NvHdRQ', 'https://www.youtube.com/watch?v=SNrbOkJLEg4&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=00sCaN0QEa0', 'https://www.youtube.com/watch?v=f3dE51libNQ', 'https://www.youtube.com/watch?v=KJ0jN9KADlA', 'https://www.youtube.com/watch?v=d_-aZTTtvV0', 'https://www.youtube.com/watch?v=gkAADEuB0Es', 'https://www.youtube.com/watch?v=qbwdd8YnS74', 'https://www.youtube.com/watch?v=qfh5kY02158', 'https://www.youtube.com/watch?v=NhfWwiFny7M', 'https://www.youtube.com/watch?v=ffeNmlAy88U', 'https://www.youtube.com/watch?v=JlG9Dh3SnOU', 'https://www.youtube.com/watch?v=tMzkRyKd7Dw', 'https://www.youtube.com/watch?v=9qcNRXt0eGc', 'https://www.youtube.com/watch?v=ZxWU4IZSWjs', 'https://www.youtube.com/watch?v=6PcdhQFYShw', 'https://www.youtube.com/watch?v=qO6nS8BYZxw', 'https://www.youtube.com/watch?v=bMSr3lrOHWY', 'https://www.youtube.com/watch?v=O0jF-aihvP0', 'https://www.youtube.com/watch?v=DnZFijxJlEg', 'https://www.youtube.com/watch?v=KPSJhGe__Tc&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=Wtjy7dBgirc', 'https://www.youtube.com/watch?v=tQdXA1AHf5U&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=mlEZZl6cwcY', 'https://www.youtube.com/watch?v=AWtBC-1VXlI', 'https://www.youtube.com/watch?v=Ngj002M_iME', 'https://www.youtube.com/watch?v=e96jo2TGzEI', 'https://www.youtube.com/watch?v=uiFF2pZ6_1U', 'https://www.youtube.com/watch?v=H-iAA09jlW0', 'https://www.youtube.com/watch?v=5GnmChMUrG4', 'https://www.youtube.com/watch?v=LiQySHy6GQ4', 'https://www.youtube.com/watch?v=UsPh7gyjyBo', 'https://www.youtube.com/watch?v=FlFquXPA6Ps&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=wNALiZm9UjM', 'https://www.youtube.com/watch?v=jM7FPhx4O64', 'https://www.youtube.com/watch?v=QoyEgiO0DjE', 'https://www.youtube.com/watch?v=aWYsKWciXjI', 'https://www.youtube.com/watch?v=jIDsYsvRF-E', 'https://www.youtube.com/watch?v=tsKUQJEcPvQ', 'https://www.youtube.com/watch?v=8XpK4mVNXWY', 'https://www.youtube.com/watch?v=LCTkoABQ7Fg', 'https://www.youtube.com/watch?v=j0y4etbegUI', 'https://www.youtube.com/watch?v=gM9lcqcHI0w&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=y0ZE8xYTutg', 'https://www.youtube.com/watch?v=tYIPAWwPf5c', 'https://www.youtube.com/watch?v=QPpd21Gns9o', 'https://www.youtube.com/watch?v=0K_AGLYvX1k', 'https://www.youtube.com/watch?v=Tf7K04WKrUc', 'https://www.youtube.com/watch?v=YaNRY2u8iVk', 'https://www.youtube.com/watch?v=xNQXBOrtf3A', 'https://www.youtube.com/watch?v=8-FrmaRNshQ', 'https://www.youtube.com/watch?v=kqFPNMqOVUs&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=pCVWNWjuZPg', 'https://www.youtube.com/watch?v=tXy8Fu4OKhk', 'https://www.youtube.com/watch?v=-9mEUh6ZnRs', 'https://www.youtube.com/watch?v=6uwmgRKTAVA', 'https://www.youtube.com/watch?v=NzjEq9Wpcvs', 'https://www.youtube.com/watch?v=F8CGA_NxZgw', 'https://www.youtube.com/watch?v=tWWo7okJcAk', 'https://www.youtube.com/watch?v=g6YxkdGvtIs', 'https://www.youtube.com/watch?v=JpR_glXl7V0', 'https://www.youtube.com/watch?v=ZReeNM1wFT8', 'https://www.youtube.com/watch?v=Xyf46arCJL8', 'https://www.youtube.com/watch?v=FbTSolwDzis', 'https://www.youtube.com/watch?v=hUO5R3ht4Lo', 'https://www.youtube.com/watch?v=bDYn3xiyd2Y', 'https://www.youtube.com/watch?v=nsYrLh4dw3w', 'https://www.youtube.com/watch?v=X__2nYwOB-s&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=7FHYEH3DWmw', 'https://www.youtube.com/watch?v=8MQki3r6D-k', 'https://www.youtube.com/watch?v=7MdqILOO-10', 'https://www.youtube.com/watch?v=V0OjuYL1GYw', 'https://www.youtube.com/watch?v=Gl6Bc3-nMHM', 'https://www.youtube.com/watch?v=pdbNquDYo9I', 'https://www.youtube.com/watch?v=YSAaC71Ay-k', 'https://www.youtube.com/watch?v=RXuUaePwaFo', 'https://www.youtube.com/watch?v=OSgaKBQMbcA', 'https://www.youtube.com/watch?v=kXflmTtL0dg', 'https://www.youtube.com/watch?v=W6ewBHFY86k&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=fT60AL2Y1bw', 'https://www.youtube.com/watch?v=CWAKhb8bLKw', 'https://www.youtube.com/watch?v=8n8mbVq1LEw', 'https://www.youtube.com/watch?v=0rhgWWW-61o', 'https://www.youtube.com/watch?v=MYgBUuWnwSc', 'https://www.youtube.com/watch?v=G4xNjy23-2k', 'https://www.youtube.com/watch?v=rwRgVF_5Urk', 'https://www.youtube.com/watch?v=axw1NrrZt0s', 'https://www.youtube.com/watch?v=Pmf4X5XcZvU', 'https://www.youtube.com/watch?v=oZmwrfFh29Y', 'https://www.youtube.com/watch?v=rXAnHPK-iCk', 'https://www.youtube.com/watch?v=E0-ARl9yNYk', 'https://www.youtube.com/watch?v=sV761D18fJs', 'https://www.youtube.com/watch?v=Y94YVsqxgZQ', 'https://www.youtube.com/watch?v=h2S1B-ncSlo', 'https://www.youtube.com/watch?v=XRSbOQQ6m3k&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=SR2wKgBnvBo', 'https://www.youtube.com/watch?v=mYYcMDd4AtY', 'https://www.youtube.com/watch?v=b4FV7YxHqKA', 'https://www.youtube.com/watch?v=Jx-d2VFZzkw', 'https://www.youtube.com/watch?v=IZXMOSkspgQ', 'https://www.youtube.com/watch?v=hkFHo0IEzRM', 'https://www.youtube.com/watch?v=kG9H5PyByJE&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=90_Z204XHJM&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=u0iS1c3HLPU', 'https://www.youtube.com/watch?v=qO3XIUESstQ', 'https://www.youtube.com/watch?v=evtQ0H3H7P4', 'https://www.youtube.com/watch?v=zB1DrUJacBM', 'https://www.youtube.com/watch?v=SYMSAujeQ_A', 'https://www.youtube.com/watch?v=teUkyHNDtBY&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=zMAtzDmb1G4', 'https://www.youtube.com/watch?v=H_yEZlwvx8o', 'https://www.youtube.com/watch?v=fMvakegcn0s', 'https://www.youtube.com/watch?v=0ZrFhWmbf54', 'https://www.youtube.com/watch?v=jxLwGDkR0lI', 'https://www.youtube.com/watch?v=Qptt2-Wq2f8', 'https://www.youtube.com/watch?v=lYfM8xwdMA4', 'https://www.youtube.com/watch?v=CU6fF5vRztM', 'https://www.youtube.com/watch?v=6Z-eXwhVgUo&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=0TKBV_gHcTI', 'https://www.youtube.com/watch?v=2zYIM0zeroA&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=uPZQR52sxxQ', 'https://www.youtube.com/watch?v=f3ut5JDnLRI', 'https://www.youtube.com/watch?v=0wJLQOf5vvY', 'https://www.youtube.com/watch?v=3TnDqFAl6FE&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=ZPc_tHMpzkE', 'https://www.youtube.com/watch?v=tNO6Y91cnt0', 'https://www.youtube.com/watch?v=DRYhAzzo5Dg', 'https://www.youtube.com/watch?v=5frQ5ea7QNQ', 'https://www.youtube.com/watch?v=UrbpMt0BDYs', 'https://www.youtube.com/watch?v=VCbX2NV55AM', 'https://www.youtube.com/watch?v=wkpegrBRucg', 'https://www.youtube.com/watch?v=ryNffeyA8Rw', 'https://www.youtube.com/watch?v=_zpSoRWEAns', 'https://www.youtube.com/watch?v=fSutSbOdUWE', 'https://www.youtube.com/watch?v=OZx25lC4z7I', 'https://www.youtube.com/watch?v=xOC8iTRDGAs', 'https://www.youtube.com/watch?v=51L2G8IuRi8', 'https://www.youtube.com/watch?v=fWMokR2mb6M', 'https://www.youtube.com/watch?v=laQja_xj3no', 'https://www.youtube.com/watch?v=Dpmr-oF14hY', 'https://www.youtube.com/watch?v=tirJ-YelUnc', 'https://www.youtube.com/watch?v=aald3_uUm_k', 'https://www.youtube.com/watch?v=yCmfm47a3y0', 'https://www.youtube.com/watch?v=c3XhlhmNpZM', 'https://www.youtube.com/watch?v=78iri5qQTKg', 'https://www.youtube.com/watch?v=4H70cRwS7k8', 'https://www.youtube.com/watch?v=TK-0Ae0Vdf4', 'https://www.youtube.com/watch?v=jDRby1KEv9o', 'https://www.youtube.com/watch?v=Oz3S0LNPIps', 'https://www.youtube.com/watch?v=q6e_QehMQKc', 'https://www.youtube.com/watch?v=QmCgbD7vrYI', 'https://www.youtube.com/watch?v=s2u5x7ESD6g', 'https://www.youtube.com/watch?v=OcvjMLgoUr8', 'https://www.youtube.com/watch?v=VIbjA5Jk7qY', 'https://www.youtube.com/watch?v=GvyH2oDfSw0', 'https://www.youtube.com/watch?v=qNEtW5I33LI', 'https://www.youtube.com/watch?v=jVnCchkP-Jw', 'https://www.youtube.com/watch?v=DDDCv4RcZkQ', 'https://www.youtube.com/watch?v=IaX-Zxyw6wM', 'https://www.youtube.com/watch?v=uNbTUkVwWHI', 'https://www.youtube.com/watch?v=rl6crZa65sY', 'https://www.youtube.com/watch?v=cCezK802Uvk', 'https://www.youtube.com/watch?v=UDHG6ydEOng', 'https://www.youtube.com/watch?v=loQbvF3SjGY',
             'https://www.youtube.com/watch?v=svyh88ftoDQ&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=PtFXHKdRhrE', 'https://www.youtube.com/watch?v=bHFFIALVkl8&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=aROlcVax4uE', 'https://www.youtube.com/watch?v=9jkAUbjWlLg', 'https://www.youtube.com/watch?v=E0uClpX3X4A&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=p-wGLCmz0lk', 'https://www.youtube.com/watch?v=rn27i-VRct4', 'https://www.youtube.com/watch?v=JNK9wX4Bx7Q', 'https://www.youtube.com/watch?v=H9ZllYNmkPE', 'https://www.youtube.com/watch?v=SN_inih_YEA', 'https://www.youtube.com/watch?v=esnaVQB2WZ8', 'https://www.youtube.com/watch?v=0DxkkLCfwpk', 'https://www.youtube.com/watch?v=Yi2GIX0dBaY&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=Y0ZPd4xNHp8', 'https://www.youtube.com/watch?v=gHXu2Q0jiIs', 'https://www.youtube.com/watch?v=rA7qsIPKw-A', 'https://www.youtube.com/watch?v=Lmz5i97_kNk', 'https://www.youtube.com/watch?v=uT2bwVrNZYM', 'https://www.youtube.com/watch?v=qHH8zw-Szno', 'https://www.youtube.com/watch?v=-oWS0CGnOKs', 'https://www.youtube.com/watch?v=vBQcco8TjnE', 'https://www.youtube.com/watch?v=g9NnK_7JI7c&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=Bls05CVTg6w', 'https://www.youtube.com/watch?v=99oB6a-BsdI', 'https://www.youtube.com/watch?v=trVJvwQ3jE4', 'https://www.youtube.com/watch?v=M8icCUhvVak', 'https://www.youtube.com/watch?v=_qEfvHvJ5X8', 'https://www.youtube.com/watch?v=kQiIrwkKTbY', 'https://www.youtube.com/watch?v=x9fzLp0kflo', 'https://www.youtube.com/watch?v=n3gb2AXuFpI', 'https://www.youtube.com/watch?v=uapxvdIovi4', 'https://www.youtube.com/watch?v=r-5LLyThUfo', 'https://www.youtube.com/watch?v=_bvnHx_9WgI&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=5WnCw1_Qkps', 'https://www.youtube.com/watch?v=kPiXRKRTkOk', 'https://www.youtube.com/watch?v=NWjUWgDamxw', 'https://www.youtube.com/watch?v=mnt6eHuROyM', 'https://www.youtube.com/watch?v=s6x1MRWfpPw', 'https://www.youtube.com/watch?v=mJ-QUx0rZtc', 'https://www.youtube.com/watch?v=VQ7DRqPk5Ic', 'https://www.youtube.com/watch?v=MfPZQRtb-hw', 'https://www.youtube.com/watch?v=GxFc7xqabpg&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=6NAgsUhwNBQ&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=a56h0wrt2oM', 'https://www.youtube.com/watch?v=igeHXGeyIzQ', 'https://www.youtube.com/watch?v=azmNpJ5rO8E', 'https://www.youtube.com/watch?v=kbXdvEksMgI', 'https://www.youtube.com/watch?v=G-fk6458ZP0', 'https://www.youtube.com/watch?v=EttkUMtQsVo', 'https://www.youtube.com/watch?v=FgbkAuYzJdE&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=aTTWkcheuyU', 'https://www.youtube.com/watch?v=ECF_mic70gI&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=3uLAcp4JKOQ', 'https://www.youtube.com/watch?v=j_Z_8WMsDYA', 'https://www.youtube.com/watch?v=juJaRn2WJRU', 'https://www.youtube.com/watch?v=jdmPsV6jP4w', 'https://www.youtube.com/watch?v=hj3ER7KqxRc', 'https://www.youtube.com/watch?v=kmOnam8Harc', 'https://www.youtube.com/watch?v=JKyGB6fMe-E', 'https://www.youtube.com/watch?v=He7QdX1OfLo', 'https://www.youtube.com/watch?v=mfVGvc4TiH4', 'https://www.youtube.com/watch?v=9drpff6aOrw', 'https://www.youtube.com/watch?v=pSyfBb0dWRU', 'https://www.youtube.com/watch?v=7VBuipv8MnY', 'https://www.youtube.com/watch?v=DLOwbP9x86E', 'https://www.youtube.com/watch?v=qjf8kgi32OQ', 'https://www.youtube.com/watch?v=4d6G1SFCUPs', 'https://www.youtube.com/watch?v=jqTlyUuhBdg', 'https://www.youtube.com/watch?v=M4V8Z0BNs8A', 'https://www.youtube.com/watch?v=EBNwun2pMNE', 'https://www.youtube.com/watch?v=saTpuYujJZ8&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=RyN0XJRzAuU', 'https://www.youtube.com/watch?v=TcvPUgG8wuw&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=mzJLAzhiRrc&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=3g_BJLbt918', 'https://www.youtube.com/watch?v=0S6E5SmpaRo', 'https://www.youtube.com/watch?v=T6wSocRSzRA', 'https://www.youtube.com/watch?v=KBHgjQWZ8vE', 'https://www.youtube.com/watch?v=bd6_pjKvSts', 'https://www.youtube.com/watch?v=vpvught1F6M', 'https://www.youtube.com/watch?v=GNwtYm9OC6g&pp=0gcJCU0KAYcqIYzv', 'https://www.youtube.com/watch?v=qeyCWplJJow', 'https://www.youtube.com/watch?v=Bv-kE4TD1TM', 'https://www.youtube.com/watch?v=Ccep1M-p-WQ', 'https://www.youtube.com/watch?v=DjhiMzuTuz4', 'https://www.youtube.com/watch?v=XIuqxWqtsJ0', 'https://www.youtube.com/watch?v=fiEmUPdaq38', 'https://www.youtube.com/watch?v=rjT14uzZvUA', 'https://www.youtube.com/watch?v=Wafetk9cQGE', 'https://www.youtube.com/watch?v=n1qM_Xpaq_M', 'https://www.youtube.com/watch?v=Qu5LWtCtQGw', 'https://www.youtube.com/watch?v=ZAyn88puKXw', 'https://www.youtube.com/watch?v=icLjcRxGjhs', 'https://www.youtube.com/watch?v=XcIzO9hsdwI&pp=0gcJCU0KAYcqIYzv'] 

class Command(BaseCommand):
    help = 'Runs the YouTube transcript scraper'

    def add_arguments(self, parser):
        # Optional: allows you to pass a specific URL
        # python manage.py run_scraper --url https://...
        parser.add_argument('-url', type=str, help='Specific YouTube URL to scrape')
        parser.add_argument('-workers', type=int, help='Number of workers to spawn(must be less than or equal to product of selenium instances & sessions)')
        parser.add_argument('-hub', type=str)

    def handle(self, *args, **options):
        url = options['url']
        hub_addr = options['hub']
        num_workers = options['workers']


        self.stdout.write(self.style.SUCCESS(f'Starting scraper for: {url} on hub {hub_addr}'))
        
        channel_name = None
        # extract channel from url
        if url:
            url_parts = url.split('/')
            for part in url_parts:
                if '@' in part:
                    channel_name = part[1:]

        # driver_options = webdriver.ChromeOptions()
        # driver_options.add_argument("mute-audio")
        # driver_options.add_argument("--windows-size=1920,1080")
        # driver_options.add_argument("--headless=new")   

        # # get videos from url
        # main_driver = webdriver.Remote(command_executor=f"http://{hub_addr}:4444", options=driver_options)
        # videos = YTScraper.find_videos(driver=main_driver, url=url, author=channel_name)
        # main_driver.quit()
        videos = VIDEOSV5[:10]
        # user threaded scraper with returned videos        
        if not num_workers or num_workers < 1 or num_workers > 30:
            num_workers = 4

        print(f"total videos: {len(videos)}")
        

        # NOTE: queue.Queue() is thread-safe
        video_queue = queue.Queue()
        for video in videos:
            video_queue.put(video)

        # assign work to threads
        print(f"assigning {num_workers} workers")

        workers = []
        for i in range(num_workers):
            try:
                new_worker = ScraperWorker(id=i, selenium_addr=hub_addr)
                workers.append(threading.Thread(target=new_worker.get_transcript_v2, args=(video_queue, test, get_transcript_fast)))
            except Exception as e:
                print(f"Failed to assign worker id:{i} {e}")
                pass
            
        # Start threads
        for worker in workers:
            worker.start()
        # Complete threads
        for worker in workers:
            worker.join()
        
        self.stdout.write(self.style.SUCCESS('Successfully scraped transcript'))