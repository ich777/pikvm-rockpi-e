#!/bin/bash
# Update from older version to PiKVM 3.296

# Upgrade packages
apt-get update
apt-get -y upgrade

# Stop PiKVM
systemctl stop kvmd kvmd-nginx

# Create temp directory and backup custom files
mkdir -p /tmp/pikvm/custom
cp /usr/lib/python3.11/kvmd/plugins/hid/_mcu/gpio.py /tmp/pikvm/custom/
cp /usr/lib/python3.11/kvmd/plugins/atx/mraa.py /tmp/pikvm/custom/
cp /usr/lib/python3.11/kvmd/aiogp.py /tmp/pikvm/custom/

# Download new PiKVM release and put files in place
wget -O pikvm.tar.xz https://git.minenet.at/ich777/pikvm-rockpi-s/raw/branch/master/sourcepkgs/kvmd-3.296-1-any.pkg.tar.xz
tar -C /tmp/pikvm -xvf pikvm.tar.xz
cp -R /tmp/pikvm/usr/bin/* /usr/bin/
cp -R /tmp/pikvm/usr/lib/python3.11/site-packages/kvmd* /usr/lib/python3.11/
cp -R /tmp/pikvm/usr/share/* /usr/share/
cp -R /tmp/pikvm/var/* /var/

# Download new ustreamer package and put files in place
wget -O ustreamer.tar.xz https://git.minenet.at/ich777/pikvm-rockpi-s/raw/branch/master/sourcepkgs/ustreamer-5.48-3-armv7h.pkg.tar.xz
tar -C /tmp/pikvm -xvf ustreamer.tar.xz
cp -R /tmp/pikvm/usr/lib/ustreamer /usr/lib/

# Patch export.py for Debian 12
sed -i 's/@async_lru.alru_cache(maxsize=1, ttl=5)/@async_lru.alru_cache()/g' /usr/lib/python3.11/kvmd/apps/kvmd/api/export.py

# Copy old custom files back
cp /tmp/pikvm/custom/gpio.py /usr/lib/python3.11/kvmd/plugins/hid/_mcu/gpio.py
cp /tmp/pikvm/custom/mraa.py /usr/lib/python3.11/kvmd/plugins/atx/mraa.py
cp /tmp/pikvm/custom/aiogp.py /usr/lib/python3.11/kvmd/

# Remove temporary directory
rm -rf /tmp/pikvm

# Start PiKVM
systemctl start kvmd-nginx
systemctl start kvmd
