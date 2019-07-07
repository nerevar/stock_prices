.PHONY: day cron download_moex download_nasdaq graphs_moex graphs_nasdaq travis-push

ifndef DAY
UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
	# Mac OS previous day with `date`:
	DAY:=$(shell date -v -1d +%Y-%m-%d)
else
	DAY:=$(shell date -d "yesterday" +%Y-%m-%d)
endif
endif

day:
	@echo "DAY passed: $(DAY)"

cron: graphs_moex graphs_nasdaq
	@echo "$(DAY) cron finished"

travis-push:
	git config --global user.email "travis@travis-ci.org"
	git config --global user.name "Travis CI"

	git checkout master
	git status
	git add quotes graph_data
	git commit quotes graph_data --message "Travis build #${TRAVIS_BUILD_NUMBER} for $(DAY)"

	git remote add origin-with-token https://nerevar:${GITHUB_TOKEN}@github.com/nerevar/stock_prices.git
	git push origin-with-token HEAD:master

download_moex:
	@echo "Download MOEX data for $(DAY)"
	python main.py download --engine stock --market bonds   --date $(DAY)
	python main.py download --engine stock --market shares  --date $(DAY)
	python main.py download --engine stock --market index   --date $(DAY)
	python main.py download --engine currency --market selt --date $(DAY)

graphs_moex: download_moex
	@echo "Buld graphs for MOEX for $(DAY)"
	python main.py graphs --date $(DAY) --graphs eurrub imoex tryrub usdrub yndx_moex sbmx_fxrl

download_nasdaq:
	@echo "Download NASDAQ data for $(DAY)"
	python main.py download --engine nasdaq --market INX --date $(DAY)
	python main.py download --engine nasdaq --market BTC --date $(DAY)
	python main.py download --engine nasdaq --market YNDX --date $(DAY)

graphs_nasdaq: download_nasdaq
	@echo "Buld graphs for NASDAQ for $(DAY)"
	python main.py graphs --date $(DAY) --clear --graphs snp_inx btc yndx_nasdaq
