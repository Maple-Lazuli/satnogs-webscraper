from bs4 import BeautifulSoup

import satnogs_webscraper.constants as cnst
import satnogs_webscraper.request_utils as ru


def get_sat_id(norad=""):
    res = ru.get_request(cnst.sat_db_address + norad)

    html_content = res.content.decode()

    soup = BeautifulSoup(html_content, 'html.parser')

    label_element = soup.find("dt", string="Satellite ID")

    if label_element:
        # 2. Find the next sibling (the <dd> tag) and get its text
        satellite_id = label_element.find_next_sibling("dd").get_text(strip=True)
        return satellite_id
    else:
        return None


if __name__ == "__main__":
    sat_id = get_sat_id("44352")
    print(sat_id)