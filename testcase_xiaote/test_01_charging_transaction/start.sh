#!/usr/bin/env bash

pipreqs . --encoding=utf8 --force
#  pip install -r requirements.txt
rm -rf report
reprot_path="../report"

array=(01)

for e in ${array[@]}; do
  echo "swipe card testcase suite_$e"
  cd test_${e}*
#  pytest test*.py --alluredir ${reprot_path} -m "need_swipe_card"
  pytest test*.py --alluredir ${reprot_path}
  cd ..
done

allure generate report/ -o report/html --clean
allure serve report/
