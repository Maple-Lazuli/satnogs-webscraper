import argparse
import os

import src.constants as cnst
import src.observation_scraper as obs
import src.observation_list_scraper as ols


def main(flags):
    cnst.verify_directories()

    obs_list_temp_dir = os.path.join(cnst.directories['observation_pages'], flags.save_name.split(".")[0])

    if os.path.isdir(obs_list_temp_dir):
        print(f"List Storage Dir: {obs_list_temp_dir}")
    else:
        os.makedirs(obs_list_temp_dir)
        print(f"List Storage Dir: {obs_list_temp_dir}")

    obs_list_scraper = ols.ObservationListFetch(url=flags.url, save_name=flags.save_name,
                                                save_dir=obs_list_temp_dir,
                                                resume=True)
    ids = obs_list_scraper.fetch_ids()

    obs_scraper = obs.ObservationScraper()

    obs_scraper.multiprocess_scrape_observations(ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--url', type=str,
                        default='https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw0&transmitter_mode=',
                        help='SATNOGS Observations List Page To Scrape')

    parser.add_argument('--save-name', type=str,
                        default='obs_list.json',
                        help='The name of the json file that will contain the observation IDs to scrape')

    parsed_flags, _ = parser.parse_known_args()

    main(parsed_flags)

    cnst.verify_directories()

