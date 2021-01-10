import logging as logger
import time as time
from bs4 import BeautifulSoup
from requests import request, status_codes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import icalendar as ical


class BaseParser(object):
    def __init__(self):
        pass

    def process(self):
        pass


class Biathlon(BaseParser):
    def __init__(self, season_year = None, event_name = None):
        super().__init__()
        self.website = f"https://www.biathlonworld.com/calendar/season/{season_year}/"
        self.event_name = event_name
        self.web_content = None
        self.webdriver = webdriver

    def get_website_content(self):
        if request("GET", self.website).status_code is not status_codes.codes.ok:
            logger.log(level=logger.ERROR, msg=f"Request on {self.website} failed with status {req.status_code}.")
            raise ConnectionError(f"Request on {self.website} failed with status {req.status_code}.")
        # Successfully continue
        logger.log(level=logger.INFO, msg=f"Request on {self.website} was successful.")

        # TODO try/except
        self.setup_webdriver()
        events = self.webdriver.find_elements_by_css_selector("h3 > a")
        logger.log(logger.DEBUG, f"Total of {len(events)} headers located on the page.")
        logger.log(logger.INFO, f"Total of {len(events)} events found.")

        self.web_content = []
        for event in events:
            event.click()
            time.sleep(1)
            page_html = self.webdriver.page_source
            self.web_content.append(BeautifulSoup(page_html, "lxml"))
            logger.log(logger.DEBUG, msg=f"Page source of event was successful and added to self.web_content")
        logger.log(logger.INFO, msg=f"Getting content of the web is complete")

    def parse(self):
        pass

    def export_to_cal(self, file_path = "Biathlon_events.ics"):
        pass

    def process(self):
        self.get_website_content()

    def setup_webdriver(self):
        opts = Options()
        # opts.add_argument("--headless")

        self.webdriver = webdriver.Chrome(options=opts, executable_path="C:\\chromedriver\\chromedriver.exe")
        self.webdriver.get(url=self.website)
        self.webdriver.find_element_by_id("cookieChoiceDismiss").click()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Biathlon, self).__exit__()
        self.webdriver.quit()


if __name__ == '__main__':
    print("Running the parsing app")
    logger.basicConfig(level=logger.DEBUG)
    parser = Biathlon(season_year=2021)
    parser.process()
