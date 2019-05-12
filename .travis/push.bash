#!/bin/bash

DAY=$1

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_website_files() {
  git add quotes graph_data
  git commit --message "Travis build $DAY: $TRAVIS_BUILD_NUMBER"
}

upload_files() {
  git remote add origin https://${GITHUB_TOKEN}@github.com/nerevar/stock_prices.git
  git push --set-upstream origin master
}

setup_git
commit_website_files
upload_files
