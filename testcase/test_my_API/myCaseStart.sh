#!/usr/bin/env bash

pipreqs . --encoding=utf8 --force
rm -rf report
echo "-*-*-*-*-*-*-*-*开始循环执行1500次【反复启停订单并软重启桩的用例】-*-*-*-*-*-*-*-*"

pytest test_Recurrent_cpVoltN.py --alluredir ./report
allure generate report/ -o report/html --clean
allure serve report/
pause
