
import argparse
from flaskr import create_node

from selenium import webdriver
import requests

def main():
    driver = webdriver.Chrome()

    # Wait for user input before closing
    while(input("Browser open. Inspect manually and press Enter to continue...") != 'quit'):
        driver.get('https://www.youtube.com/watch?v=XhluFjFAo4E')
        driver.delete_all_cookies()

    # Now continue your script or close the driver
    driver.quit()

def test_send():
    worker_addr = ''
    payload = dict()
    payload["videos"] = ["a", "b", "c", "d", "e", "f"]
    res = requests.put(f"http://{worker_addr}:5000/", json=payload)
    print(res.json())



   

def assign_work():
    """Determine whether to treat this instance as a master or worker node"""
    
    p = argparse.ArgumentParser()
    p.add_argument('--threads', type=int, default=4, help="Number of threads to run")
    group = p.add_mutually_exclusive_group()
    group.add_argument('-d', '--distr', type=str, help="Comma separated addresses to other machines")
    options, _ = p.parse_known_args()

  
    node = create_node()
    
    node.run(host="0.0.0.0")

if __name__ == "__main__":
    # main()
    assign_work()
    # test_send()