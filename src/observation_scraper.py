from os.path import exists

import hashlib
import json
from multiprocessing import Pool
import os

from bs4 import BeautifulSoup as bs
import html5lib

import src.constants as cnst
import src.image_utils as iu
import src.request_utils as ru


class ObservationScraper:
    def __init__(self, fetch_waterfalls=True, fetch_logging=True, prints=True):
        """
        Scrapes the webpages for satellite observations. Waterfall fetches are set to false by default due to the
        very large file sizes.
        :param fetch_waterfalls: Boolean on whether to pull the waterfalls from the observations
        :param fetch_logging: Boolean for logging the fetches
        :param prints: Boolean for printing output in operation.
        """
        self.observations_list = []
        self.fetch_waterfalls = fetch_waterfalls
        self.fetch_logging = fetch_logging
        self.json_file_loc = cnst.files["observation_json"]
        self.observation_save_dir = cnst.directories['observations']
        self.log_file_loc = cnst.files["log_file"]
        self.waterfall_path = cnst.directories['waterfalls']
        self.prints = prints
        cnst.verify_directories()

    def multiprocess_scrape_observations(self, observations_list, write_disk=True):
        """
        Functions similar to scrape_observations, but does multiple simultaneously
        :param observations_list: The list of observations to scrape
        :param write_disk: Boolean on whether to write for disk
        :return: None. Updates the instantiated object's observations_list
        """
        urls = [f'{cnst.web_address}{cnst.observations}{observation}/' for observation in observations_list]
        pool = Pool()
        self.observations_list = pool.map(self.scrape_observation, urls)

        return self.observations_list

    def scrape_observation(self, url):
        """
        Scrapes a webpage for an observation
        :param url: The url to the website to scrape
        :return: A dictionary of the scraped webpage
        """
        # TODO Test to see if the observation has already been scraped

        template = cnst.observation_template.copy()
        r = ru.get_request(url)
        observation = url.split("/")[-2]
        if self.fetch_logging:
            with open(self.log_file_loc, 'a') as log:
                log.writelines(f'URL: {url} \n')
                log.writelines(f'status: {r.status_code} \n')
                log.writelines(f'header: {r.headers} \n')

        if r.status_code != 200:
            print(f"Non 200 Status for {url}") if self.prints else None
            return template

        observation_web_page = bs(r.content, "html5lib")
        front_line_divs = observation_web_page.find_all("div", class_='front-line')

        for div in front_line_divs:
            key, value = self.scrape_div(div)
            if key is not None:
                template[key] = value

        waterfall_status = observation_web_page.find(id="waterfall-status-label")
        if waterfall_status is not None:
            template['Waterfall_Status'] = " ".join(
                [piece.strip() for piece in waterfall_status.attrs['title'].split("\n")])

        status = observation_web_page.select("#rating-status > span")
        if (status is not None) & (status[0] is not None):
            template['Status'] = status[0].text.strip()
            template['Status_Message'] = status[0].attrs['title'].strip()
        template['Observation_id'] = observation

        # TODO SAVE THE SCRAPE TO THE DISK
        print(f"Successful scrape for {url}") if self.prints else None

        return template

    def scrape_div(self, div):
        """
        Processes an HTML div container element and determines which part of the observation the
        div contains data for.
        :param div: HTML DiV
        :return: Key, Value pair
        """
        contents = str(div)

        # TODO - Scrape Up and Down times

        if contents.find("Satellite") != -1:
            element = div.find("a")
            return "Satellite", element.text.strip() if element is not None else None

        if contents.find("Station") != -1:
            element = div.find("a")
            return "Station", element.text.strip() if element is not None else None

        if contents.find("Transmitter") != -1:
            element = div.find("span", class_='front-data')
            return "Transmitter", element.text.strip() if element is not None else None

        if contents.find("Frequency") != -1:
            element = div.find("span", class_='front-data')
            return "Frequency", element.attrs['title'].strip() if element is not None else None

        if contents.find("Mode") != -1:
            return "Mode", [span.text.strip() for span in div.select(".front-data > span") if span is not None]

        if contents.find("Metadata") != -1:
            element = div.find("pre")
            return "Metadata", element.attrs['data-json'] if element is not None else None

        if contents.find("Downloads") != -1:
            audio = None
            waterfall = None
            waterfall_hash_name = None
            waterfall_shape = None
            for a in div.find_all("a", href=True):
                if str(a).find("Audio") != -1:
                    audio = a.attrs['href']
                if str(a).find("Waterfall") != -1:
                    waterfall = a.attrs['href']
                    waterfall_hash_name = f'{hashlib.sha256(bytearray(waterfall, encoding="utf-8")).hexdigest()}.png'
                    if self.fetch_waterfalls:
                        waterfall_shape, waterfall_hash_name = self.fetch_waterfall(waterfall, waterfall_hash_name)
            return 'Downloads', {'audio': audio, "waterfall": waterfall, "waterfall_hash_name": waterfall_hash_name,
                                 "waterfall_shape": waterfall_shape}
        return None, None

    def fetch_waterfall(self, url, file_name):
        """
        Fetches and writes waterfall PNGs to the disk, then crops the image and converts it to grey scale.
        :param url: The URL to the waterfall file to pull
        :param file_name: The name the file should be saved as.
        :return: The shape of the cropped image and name of the waterfall written to disk as a bytes object.
        """
        res = ru.get_request(url)
        waterfall_name = self.waterfall_path + file_name

        with open(waterfall_name, 'wb') as out:
            out.write(res.content)

        cropped_shape, bytes_name = iu.crop_and_save_psd(waterfall_name)

        return cropped_shape, bytes_name


if __name__ == '__main__':
    # Demonstration of use
    print("Single Scrapes")
    scraper = ObservationScraper()
    scrape1 = scraper.scrape_observation('https://network.satnogs.org/observations/5025420/')
    scrape2 = scraper.scrape_observation('https://network.satnogs.org/observations/44444/')
    print(scrape2)
    print(f"{scrape1}")
    print(f"{scrape2}")
    print("Observations Pull")
    scraper.scrape_observations([5025420, 44444])
    print("Multiprocess Observations Pull")
    scraper.multiprocess_scrape_observations([5025420, 44444])
