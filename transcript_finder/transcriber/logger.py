import threading
import mysql.connector.cursor
from mysql.connector import pooling
from abc import ABC, abstractmethod

class Logger(ABC):
    @abstractmethod
    def log(self):
        pass
    @abstractmethod
    def log_err(self):
        pass

class DBLogger(Logger):
    def __init__(self,connector : pooling.MySQLConnectionPool):
        self.conn_pool = connector
    
    def log(self):
        raise NotImplementedError

    def log_err(self):
        raise NotImplementedError
    
    def log_channel(self, channel_name) -> int:
        """Add channel to DB if it does not exist"""
        conn = self.conn_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM transcript_finder_app_channel WHERE transcript_finder_app_channel.name = '{channel_name}'")
        channel_id = cursor.fetchone()
        if not channel_id:
            cursor.execute(f"INSERT INTO transcript_finder_app_channel(name) VALUES ('{channel_name}')")
            channel_id = cursor.lastrowid
            conn.commit()
        # return connection back to pool
        cursor.close()
        conn.close()
        return channel_id 
    
    def does_video_exist(self, url):
        conn = self.conn_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM transcript_finder_app_video WHERE transcript_finder_app_video.url = '{url}'")
        res = cursor.fetchone()
        cursor.close()
        conn.close()

        return res

    def log_video(self, channel_id, url, title, date):
        conn = self.conn_pool.get_connection()
        cursor = conn.cursor()
       
      
        query = "INSERT INTO transcript_finder_app_video(url, title, channel_id, date) VALUES (%s, %s, %s, %s)"
        if isinstance(channel_id, tuple):
            channel_id = channel_id[0]
        cursor.execute(query, (url, title, channel_id, date))
        
        conn.commit()
        # print("logged video", url)
        
        cursor.close()
        conn.close()
        return cursor.lastrowid
    
    def log_transcript(self, video_id, transcript):
        conn = self.conn_pool.get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO transcript_finder_app_transcript (transcript, video_id) VALUES (%s, %s)"
        cursor.execute(query, (transcript, video_id))

        conn.commit()
        cursor.close()
        conn.close()



        


class LocalLogger(Logger):
    def __init__(self, filepath, error_filepath, dir=None):
        self.write_lock = threading.Lock()
        self.err_lock = threading.Lock()
        self.file = filepath
        self.error_file = error_filepath

        if dir is not None:
            self.file = f"{dir}/{filepath}"
            self.error_file = f"{dir}/{error_filepath}"

    def log(self, content):
        """write to main file"""
        with self.write_lock:
            # write matches to file
            with open(self.file, "a") as f:
                if isinstance(content, list):
                    for item in content:
                        f.write(item)
                else:
                    f.write(content)

    def log_err(self, content):
        """write to error file"""
        with self.err_lock:
            with open(self.error_file, "a") as err:
                err.write(content)

                

        