import argparse
import multiprocessing
import os

import satnogs_webscraper.constants as cnst
import satnogs_webscraper.observation_scraper as obs
import satnogs_webscraper.observation_list_scraper as ols
from satnogs_webscraper.observation_dataset import save_dataset


def main(flags):
    cnst.verify_directories()

    obs_list_temp_dir = os.path.join(cnst.directories['observation_pages'], flags.save_name.split(".")[0])
    save_name = os.path.join(cnst.directories['data'], flags.save_name)
    if os.path.isdir(obs_list_temp_dir):
        print(f"List Storage Dir: {obs_list_temp_dir}")
    else:
        os.makedirs(obs_list_temp_dir)
        print(f"List Storage Dir: {obs_list_temp_dir}")

    obs_list_scraper = ols.ObservationListFetch(url=flags.url, save_name=save_name,
                                                save_dir=obs_list_temp_dir,
                                                resume=True,
                                                cpus=flags.list_scrape_cpus,
                                                page_limit=flags.page_limit)
    ids = obs_list_scraper.fetch_ids()
    print("Finished Page List Scraping")
    print("Starting Observation Page Scrape")
    obs_scraper = obs.ObservationScraper(cpus=flags.obs_scrape_cpus, grey_scale=flags.grey_scale)
    obs_scraper.multiprocess_scrape_observations(ids)
    print("Finished Observation Scrape")
    print("Creating CSV")
    save_dataset(ids, save_name=f"{save_name}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--url', type=str,
                        default='https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw0&transmitter_mode=',
                        help='SATNOGS Observations List Page To Scrape')

    parser.add_argument('--save-name', type=str,
                        default='obs_list.json',
                        help='The name of the json file that will contain the observation IDs to scrape')

    parser.add_argument('--list-scrape-cpus', type=int,
                        default=1,
                        help='The number of CPUs to use for scraping observation lists')

    parser.add_argument('--obs-scrape-cpus', type=int,
                        default=multiprocessing.cpu_count(),
                        help='The number of CPUs to use for scraping observation pages')

    parser.add_argument('--page-limit', type=int,
                        default=0,
                        help='The limit on the number of observation list pages to fetch')

    parser.add_argument('--grey-scale', type=bool,
                        default=True,
                        help='Convert the psd to grey scale.')

    parsed_flags, _ = parser.parse_known_args()

    main(parsed_flags)
