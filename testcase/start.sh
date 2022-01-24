#!/usr/bin/env bash

#cd ..
#pip install -r requirements.txt
#cd testcase

#python -m pip install --upgrade pip || python3 -m pip install --upgrade pip # 更新pip工具
#pip install -r requirements.txt

rm -rf report  # 删除上一次的allure报告
reprot_path="../report"

# 执行的测试目录
array=(01 02 03 04 05 06 07 08 09 10
        11 12 13 14 15 16 17 18 19
        20 21 23 25)

if [[ $# -gt 1 ]]; then
  echo "默认（没有参数）：执行全量用例；1：执行需要刷卡的用例；2：执行不需要刷卡的用例"
  echo "参数个数错误，脚本退出！"
  exit 1
fi

# 参数值为1时，执行需要刷卡的用例
if [[ $# -eq 0 || $# -eq 1 && $1 -eq 1 ]]; then
  echo "需要刷卡测试用例"
  for e in ${array[@]}; do
  echo "执行需要刷卡测试套_$e"
  cd test_2_${e}*
  pytest test*.py --alluredir ${reprot_path} -m "need_swipe_card"
  cd ..
  done


# 参数值为2时，执行不需要刷卡的用例
elif [[ $# -eq 0 || $# -eq 1 && $1 -eq 2 ]]; then
  echo "不需要刷卡测试用例"
  for e in ${array[@]}; do
  echo "执行不需要刷卡测试套_$e"
  cd test_2_${e}*
  pytest test*.py --alluredir ${reprot_path} -m "not need_swipe_card"
  cd ..
  done

else
  echo "默认（没有参数）：执行全量用例；1：执行需要刷卡的用例；2：执行不需要刷卡的用例"
  echo "参数值错误，脚本退出！"
  exit 1
fi

allure generate report/ -o report/html --clean
allure serve report/ # 生成allure 报告服务
exit 0
