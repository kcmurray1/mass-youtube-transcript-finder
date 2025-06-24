
import argparse
from flaskr import create_node



from selenium import webdriver

def main():
    driver = webdriver.Chrome()

    # Wait for user input before closing
    while(input("Browser open. Inspect manually and press Enter to continue...") != 'quit'):
        driver.get('https://www.youtube.com/watch?v=XhluFjFAo4E')
        driver.delete_all_cookies()

    # Now continue your script or close the driver
    driver.quit()


def assign_work():
    """Determine whether to treat this instance as a master or worker node"""
    
    p = argparse.ArgumentParser()
    p.add_argument('--threads', type=int, default=4, help="Number of threads to run")
    group = p.add_mutually_exclusive_group()
    group.add_argument('--test', action='store_true', help="Determine whether to run system test suite")
    group.add_argument('-d', '--distr', type=str, help="Comma separated addresses to other machines")
    options, _ = p.parse_known_args()

    # Run Test Suite
    if options.test:
    
        return
    
    node = create_node(
        is_master=options.distr != None,
        num_threads=options.threads,
        worker_addr_list=options.distr
    )

    # node.run(host="0.0.0.0")

if __name__ == "__main__":
    main()
    # assign_work()