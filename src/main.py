import os
import src.constants as cnst
import src.observation_scraper as obs
import src.observation_list_scraper as ols

if __name__ == "__main__":
    bad_signals = "https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw0&transmitter_mode="
    unknown_signals = "https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rwu&transmitter_mode="
    good_signals = "https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw1&transmitter_mode="

    bad_name = os.path.join(cnst.directories['observation_pages'], "bad.json")
    bad_obs_list = ols.ObservationListFetch(url=bad_signals, save_name=bad_name, save_dir=cnst.directories["bad"],
                                            resume=True, page_limit=5)
    bad_obs_ids = bad_obs_list.fetch_ids()

    unk_name = os.path.join(cnst.directories['observation_pages'], "unk.json")
    unk_obs_list = ols.ObservationListFetch(url=unknown_signals, save_name=unk_name,
                                            save_dir=cnst.directories["unknown"],
                                            resume=True, page_limit=5)
    unk_obs_ids = unk_obs_list.fetch_ids()

    good_name = os.path.join(cnst.directories['observation_pages'], "unk.json")
    good_obs_list = ols.ObservationListFetch(url=good_signals, save_name=good_name, save_dir=cnst.directories["good"],
                                             resume=True, page_limit=5)
    good_obs_ids = good_obs_list.fetch_ids()

    scraper = obs.ObservationScraper()
    scraper.multiprocess_scrape_observations(bad_obs_ids)
    scraper.multiprocess_scrape_observations(unk_obs_ids)
    scraper.multiprocess_scrape_observations(good_obs_ids)

