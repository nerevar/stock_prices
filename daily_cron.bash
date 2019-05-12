#!/bin/bash

# daily cron: download stocks data & plot graphs
# run: /bin/bash daily_cron.bash `date +%Y-%m-%d`

DAY=$1

python main.py download --engine stock --market bonds   --date $DAY
python main.py download --engine stock --market shares  --date $DAY
python main.py download --engine stock --market index   --date $DAY
python main.py download --engine currency --market selt --date $DAY

python main.py graphs --date $DAY --graphs eurrub moex tryrub usdrub yndx_moex

# python main.py download --engine nasdaq --market INX --date $DAY
# python main.py download --engine nasdaq --market BTC --date $DAY
# python main.py download --engine nasdaq --market YNDX --date $DAY

# python main.py graphs --date $DAY --clear --graphs snp_inx btc yndx_nasdaq
