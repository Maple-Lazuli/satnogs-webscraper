source venv/bin/activate
python -m src.main --cpus 2 --save-name good.json --page-limit 5 --url "https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw1&transmitter_mode="
