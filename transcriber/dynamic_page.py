from selenium import webdriver
from transcriber.utils.constants.paths import Paths
import pyautogui
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PAGELOADTIME = 10
WAIT_TIME_TRANSCRIPT_LOAD = 10
WAIT_TIME_BUTTON_LOAD = 10

class DynamicPage:
    """Class of methods that logic on dynamic html element(clicking, scrolling, etc)"""

    def scroll_to_bottom(video_count: int):
        """Scroll to the bottom of a webpage based on the video_count
        Args:
            video_count: an int descripting 
        NOTE: Youtube initially renders 30 videos.
            Performing bottom scroll renders up to an additional 30 videos(if present).
        """
        print("rendering videos...")

        # Perform one scroll to the bottom of the webpage to handle
        # A bug where prescence of video elements are obscured by Chrome pop-ups
        pyautogui.hotkey("ctrl", "end")
        time.sleep(3)

        # Scroll to the bottom for every additional 30 videos
        if video_count:
            num_bottom_scroll = ((video_count - 30) // 30)
            if num_bottom_scroll < 0:
                num_bottom_scroll = 1
            print(f"scrolling {num_bottom_scroll} times")
            for _ in range(num_bottom_scroll):
                pyautogui.hotkey("ctrl", "end")
                time.sleep(3)
        else:
            print("no video_count: ", video_count, flush=True)

    
    def get_transcript(driver : webdriver.Chrome, ignore_desc_btn=False):
        try:
            if not ignore_desc_btn:
                # Wait until description element is visible
                button_description = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
                EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_DESCRIPTION))         
                )
                button_description.click()
            # Wait until transcript button is visible
            button_transcript = WebDriverWait(driver, WAIT_TIME_BUTTON_LOAD).until(
                EC.element_to_be_clickable((By.XPATH, Paths.XPATH_BUTTON_TRANSCRIPT))
            )
            button_transcript.click()
            # Wait for transcript content elements to load
            transcript_lines = WebDriverWait(driver, WAIT_TIME_TRANSCRIPT_LOAD).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, Paths.CSS_TEXT_TRANSCRIPT))
            )
         
            # Return transcript lines that contain specified phrase
            return transcript_lines
        except Exception as e:
            return e    
    

   