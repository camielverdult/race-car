#!/usr/bin/env bash

# This scripts install all the prerequisites for the RaceX car to run 
apt install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran python3-dev python3-pip -y

cd /home/pi
wget -O opencv.zip https://github.com/opencv/opencv/archive/refs/tags/4.5.2.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/refs/tags/4.5.2.zip

unzip -o opencv.zip
# opencv-4.5.2 

unzip -o opencv_contrib.zip
# opencv_contrib-4.5.2

echo "CONF_SWAPSIZE=2048" > /etc/dphys-swapfile

/etc/init.d/dphys-swapfile stop
/etc/init.d/dphys-swapfile start

python3 -m pip install numpy

cd /home/pi/opencv-4.5.2 
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/home/pi/opencv_contrib-4.5.2/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D CMAKE_SHARED_LINKER_FLAGS=-latomic \
    -D BUILD_EXAMPLES=OFF ..

make -j4
make install
ldconfig

apt autoremove

echo "CONF_SWAPSIZE=100" > /etc/dphys-swapfile

/etc/init.d/dphys-swapfile stop
/etc/init.d/dphys-swapfile start

python3 -m pip install -r pip_requirements.txt