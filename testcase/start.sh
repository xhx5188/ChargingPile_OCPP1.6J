#!/usr/bin/env bash

#rm -rf *.log
#log_name=$(date +%s)
#log_name=${log_name}.log
#touch ${log_name}


cd test_2_01*
pytest -sv test*.py
cd ..

cd test_2_02*
pytest -sv test*.py
cd ..

cd test_2_03*
pytest -sv test*.py
cd ..

