## 12/20/24
- Reverted screen sizing to default due to an element retrieval bug when using a custom screen size
- Updated XPATH_BUTTON_DESCRIPTION and XPATH_BUTTON_TRANSCRIPT from outdated paths

## 1/17/2025
- reorganized flask endpoint route from "/" to "/internal"
- redsigned old flask implementation

## 6/16/2025
- Changed testing from Unittest package to Pytest
- Added Django project for future use of current project

## 6/18/2025
- Removed TranscriptProcessor implementation and separated logic into DynamicPage and StaticPage
  classes that will be used in a refactored Multithread implementation

## July 2025
- Replaced Flask implementation with Selenium-Grid Docker solution
- Redesigned system where Local machine cluster webscrapes and updates MySQL database. The Django frontend will have access to the
  Database and display the information
- Created ScraperWorker and ScraperThreaded class that uses remote Selenium Webdriver to connect to Selenium-Grid
- Created docker-compose file to setup machine hosting the Selenium-Grid

## 8/5/2025
- Commenced API first design for frontend interaction with MySQL database
    - created web.py to handle frontend rendering, leaving views.py to handle API interaction
- Create Home page that displays Channels and number of recorded videos
- removed old Flask Node implementation
