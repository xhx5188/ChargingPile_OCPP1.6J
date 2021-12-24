#!/usr/bin/env bash

#  pipreqs . --encoding=utf8 --force
#  pip install -r requirements.txt
rm -rf report
reprot_path="../report"

cd test_2_01*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_02*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_03*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_04*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_05*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_06*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_07*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_08*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_09*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_10*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_11*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_12*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_13*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_14*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..



cd test_2_16*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_17*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_18*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

#cd test_2_20*
#pytest -sv test*.py --alluredir ${reprot_path}
#cd ..

cd test_2_21*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

cd test_2_23*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..


cd test_2_25*
pytest -sv test*.py --alluredir ${reprot_path}
cd ..

allure generate report/ -o report/html --clean
allure serve report/