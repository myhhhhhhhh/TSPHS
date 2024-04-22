#!/bin/bash

cd tsp2d_lib
make clean
make -j
cd ..
./run_eval.sh