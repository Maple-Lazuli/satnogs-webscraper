from dataclasses import dataclass
from enum import Enum


class Results(Enum):
    IGNORE = -1
    ON = 1
    OFF = 0


class Artifacts(Enum):
    IGNORE = -1
    NON_RATED = 0
    WITH_SIGNAL = 1
    WITHOUT_SIGNAL = 2


@dataclass
class Scraper:
    norad: str = "25544"  # Norad number for the ISS
    future: bool = False
    good: bool = True
    bad: bool = False
    unknown: bool = False
    failed: bool = False
    observer: str = ''
    station_id: str = ''  # The numeric designator for a station
    waterfall: object = -1  # Results Enum
    audio: object = -1  # Results Enum
    data: object = -1  # Results Enum
    start: str = ''
    end: str = ''
    artifacts: object = -1
    # TODO PAGE LIMIT
    # TODO PAGE LIMIT

    def __post_init__(self):
        self.waterfall = Results(self.waterfall)
        self.audio = Results(self.audio)
        self.data = Results(self.data)
        self.artifacts = Artifacts(self.artifacts)

    def generate_query_string(self):
        url = ['https://network.satnogs.org/observations/?']
        if not self.future:
            url.append('future=0')

        if not self.good:
            url.append('good=0')

        if not self.bad:
            url.append('bad=0')

        if not self.unknown:
            url.append('unknown=0')

        if not self.failed:
            url.append('failed=0')

        url.append(f'observer={self.observer}')

        url.append(f'station={self.station_id}')

        if self.waterfall != Results.IGNORE:
            if self.waterfall == Results.ON:
                url.append('results=w1')
            elif self.waterfall == Results.OFF:
                url.append('results=w0')

        if self.audio != Results.IGNORE:
            if self.audio == Results.ON:
                url.append('results=a1')
            elif self.audio == Results.OFF:
                url.append('results=a0')

        if self.data != Results.IGNORE:
            if self.data == Results.ON:
                url.append('results=d1')
            elif self.data == Results.OFF:
                url.append('results=d0')

        url.append(f'start={self.start}')
        url.append(f'end={self.end}')
        url.append(f'transmitter_mode=')

        return "&".join(url)



if __name__ == '__main__':
    scraper = Scraper()
    print(scraper.generate_query_string())

