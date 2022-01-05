#!/usr/bin/env bash

pipreqs . --encoding=utf8 --force
#  pip install -r requirements.txt
rm -rf report
reprot_path="../report"

array=(01 02 03 04 05 06 07 08 09 10
        11 12 13 14 15 16 17 18 19
        20 21 23 25)

echo ""
echo ""
echo "excute the testcases that need swipe card"
echo ""
echo ""

#执行需要刷卡用例
for e in ${array[@]}; do
  echo "swipe card testcase suite_$e"
  cd test_2_${e}*
#  pytest test*.py --alluredir ${reprot_path} -m "need_swipe_card"
  cd ..

done

echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo "excute the testcases that not need swipe card"
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
#执行不需要刷卡用例
for e in ${array[@]}; do
  echo "no swipe card testcase suite_$e"
  cd test_2_${e}*
  pytest test*.py --alluredir ${reprot_path} -m "not need_swipe_card"
  cd ..
done

allure generate report/ -o report/html --clean
allure serve report/
