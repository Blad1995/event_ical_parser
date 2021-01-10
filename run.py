from collections import namedtuple
import logging as logger
import time as time
from datetime import datetime
from bs4 import BeautifulSoup
from requests import request, status_codes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pickle as pickle
import icalendar as ical


class BaseParser(object):
    Event = namedtuple("Event", field_names=["time", "name", "url", "place", "note"], defaults=["", "", "", "", ""])

    def __init__(self):
        pass

    def process(self):
        pass

    def export_to_cal(self, file_path = "Events.ics"):
        calendar = ical.Calendar()
        for event in self.parsed_events:
            new_event = ical.Event()
            start_time = datetime.strptime(event.time, "%d %b %Y %H:%M")
            new_event["dtstart"] = ical.vDatetime(start_time).to_ical()
            new_event["summary"] = event.name
            new_event["description"] = f"{event.url}\n" + event.note
            calendar.add_component(new_event)

        with open(file_path, "wb") as f:
            f.write(calendar.to_ical())
            logger.log(logger.INFO, f"Successfully created {file_path} file")


class Biathlon(BaseParser):
    def __init__(self, season_year: int = None, event_name: str = None):
        super().__init__()
        self.website: str = f"https://www.biathlonworld.com/calendar/season/{season_year}/"
        self.event_name: str = event_name
        self.web_content: BeautifulSoup or None = None
        self.webdriver: webdriver = webdriver
        self.parsed_events = []

    def get_website_content(self):
        if request("GET", self.website).status_code is not status_codes.codes.ok:
            logger.log(level=logger.ERROR, msg=f"Request on {self.website} failed with status {req.status_code}.")
            raise ConnectionError(f"Request on {self.website} failed with status {req.status_code}.")
        # Successfully continue
        logger.log(level=logger.INFO, msg=f"Request on {self.website} was successful.")

        # TODO try/except
        self.setup_webdriver()
        # events = self.webdriver.find_elements_by_css_selector("h3 > a")
        # select only non expanded events
        events = self.webdriver.find_elements_by_xpath("//a[contains(@class,'js-title collapsed')]")
        logger.log(logger.DEBUG, f"Total of {len(events)} headers located on the page.")
        logger.log(logger.INFO, f"Total of {len(events)} events found.")

        self.web_content = []
        for event in events:
            # explicit wait
            time.sleep(0.1)
            event.click()
        time.sleep(0.25)
        page_html = self.webdriver.page_source
        self.web_content = BeautifulSoup(page_html, "lxml")
        logger.log(logger.DEBUG, msg=f"Page source of event was successful and added to self.web_content")
        logger.log(logger.INFO, msg=f"Getting content of the web is complete")

    def parse(self):
        events = self.web_content.find_all("li", {"class": "dcm-competition"})
        if len(events) is 0:
            logger.log(logger.WARNING, "No events found")
        else:
            logger.log(logger.INFO, f"{len(events)} events were found)")
        for event in events:
            time_str = event.find("span", {"class": "dcm-date"}).text
            event_name = event.find("span", {"class": "dcm-competition--name"}).text
            self.parsed_events.append(Biathlon.Event(name=event_name, time=time_str))

    def process(self):
        if not self.web_content:
            self.get_website_content()

        self.parse()
        self.export_to_cal(file_path="Biathlon_events.ics")

    def setup_webdriver(self):
        opts = Options()
        opts.add_argument("--headless")
        # opts.add_argument("--incognito")

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
