source venv/bin/activate
python -m src.main --cpus 20 --save-name bad.json --page-limit 5 --url "https://network.satnogs.org/observations/?future=0&failed=0&norad=&observer=&station=&start=&end=&rated=rw0&transmitter_mode="
