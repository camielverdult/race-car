#!/usr/bin/env bash

# This scripts install all the prerequisites for the RaceX car to run 
apt install cmake openssl -y
export OPENSSL_ROOT_DIR=$(whereis openssl)
python3 -m pip install -r pip_requirements.txt