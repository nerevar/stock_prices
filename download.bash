time python main.py download --engine stock --market bonds   --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine stock --market shares  --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine stock --market index   --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine currency --market selt --date 2019-03-30 --dateend 2019-05-11

time python main.py download --engine nasdaq --market YNDX --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine nasdaq --market BTC --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine nasdaq --market FB --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine nasdaq --market GOOG --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine nasdaq --market MSFT --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine nasdaq --market AMZN --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine nasdaq --market INX --date 2019-03-30 --dateend 2019-05-11
time python main.py download --engine nasdaq --market NDAQ --date 2019-03-30 --dateend 2019-05-11

time python main.py graphs --date 2019-03-30 --clear --graphs snp_inx btc yndx_nasdaq
time python main.py graphs --date 2019-03-30 --dateend 2019-05-08 --graphs eurrub moex tryrub usdrub yndx_moex
