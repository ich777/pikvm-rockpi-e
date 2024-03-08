Source files: https://files.pikvm.org/repos/arch/rpi4/  
  
**DISCLAIMER:** This project is not related to PiKVM, use at your own risk!
  
### What this is:
This repository contains everything that you can turn your RockPi E into a PiKVM with HID support with the help from a Raspberry Pi Pico.  
Please Note that only KVM functionality is implemented.  
**ATTENTION:** By default everything is running as root so please be careful and use this only for home usage or through a safe tunnel if you are using it over the internet!  
  
  
### First Steps:
1) Download Armbian for your RockPi E and put on the SD - [Download Mirror](https://github.com/ich777/pikvm-rockpi-e/releases/download/23.11.1_6.1.63/Armbian_23.11.1_Rockpi-e_bookworm_current_6.1.63_minimal.img.xz)  
2) Boot into armbian and login with ssh, username: `root` passwd: `1234`  
Please note that you first can only boot with the 100Mbit/s NIC, after the reboot the 1Gbit/s NIC will be working.  
3) Change the password for root and right after that press `CTRL + C` to drop to the shell  
4) Please also see the file [wiring_diagram.png](https://github.com/ich777/pikvm-rockpi-e/blob/master/rockpi_e_wiring_diagram.png) on how to set up the connection to the Rasperry Pi Pico (and ATX connector)  
(To flash your Pico download [this](https://github.com/ich777/pikvm-rockpi-s/raw/master/pi-pico-fw/pico-hid.uf2) file, press and hold the button on the Pico while connecting to your PC and place the file in the Picos Disk that will appear, safely eject the Pico and disconnect it from your PC)  
5) Follow the script below  
6) Connect through the browser to the IP from your RockPi and login with Username: `admin` Password: `admin`
  
### BOM:  
- RockPi E v1.21
- Raspberry Pi Pico
- HDMI-USB Capture Stick (preferably MacroSilicon USB Video - 534d:2109)
- Micro SD Card min. 8GB
- Diode 1N5819 (recommended - not strictly needed)
- Jumper wires
- Cables
  
### Install script:

```
# Disable heartbeat LED on the RockPi E to not get blind during installation
echo 0 > /sys/devices/platform/leds/leds/blue\:/brightness

# Update packages
apt-get update

# Upgrade all existing packages
apt-get -y upgrade

# Install dependencies
apt-get -y install iptables ustreamer python3 python3-systemd python3-pil \
  python3-xlib python3-zstandard python3-async-lru python3-cachetools python3-aiofiles \
  python3-pyotp python3-aiohttp python3-setproctitle python3-dbus-next \
  python3-systemd python3-passlib python3-libgpiod python3-serial libtesseract5 libxkbcommon0 nginx janus \
  git build-essential swig4.0 cmake libnode-dev python3-dev pkg-config swig tesseract-ocr \
  tesseract-ocr-ara tesseract-ocr-bel tesseract-ocr-chi-sim tesseract-ocr-ces tesseract-ocr-dan tesseract-ocr-deu \
  tesseract-ocr-eng tesseract-ocr-spa tesseract-ocr-est tesseract-ocr-fil tesseract-ocr-fao tesseract-ocr-fra \
  tesseract-ocr-hrv tesseract-ocr-hun tesseract-ocr-isl tesseract-ocr-ita tesseract-ocr-jpn tesseract-ocr-lav \
  tesseract-ocr-lat tesseract-ocr-mkd tesseract-ocr-nld tesseract-ocr-nor tesseract-ocr-pol tesseract-ocr-por \
  tesseract-ocr-pus tesseract-ocr-rus tesseract-ocr-slk tesseract-ocr-slv tesseract-ocr-tha tesseract-ocr-tur

# Disable all kvmd services during setup
systemctl disable nginx janus

# Link python3 binary so that it globally available through python
ln -s /usr/bin/python3 /usr/bin/python

# Create temporary directory
mkdir -p /tmp/pikvm
cd /tmp/pikvm

# Download and compile mraa
git clone -b master https://github.com/ich777/mraa
cd /tmp/pikvm/mraa
mkdir build
cd build/
cmake ..
make
make install
ldconfig

# Get base packages from PiKVM and extract all necessary files
wget -O pikvm.tar.xz https://github.com/ich777/pikvm-rockpi-s/raw/master/sourcepkgs/kvmd-3.296-1-any.pkg.tar.xz
tar -C /tmp/pikvm -xvf pikvm.tar.xz
cp -R /tmp/pikvm/usr/bin/* /usr/bin/
cp -R /tmp/pikvm/usr/lib/python3.11/site-packages/kvmd* /usr/lib/python3.11/
cp -R /tmp/pikvm/usr/share/* /usr/share/
cp -R /tmp/pikvm/var/* /var/
cp -R /tmp/pikvm/etc/* /etc/

# Get ustreamer package and extract it
wget -O ustreamer.tar.xz https://github.com/ich777/pikvm-rockpi-s/raw/master/sourcepkgs/ustreamer-5.48-3-armv7h.pkg.tar.xz
tar -C /tmp/pikvm -xvf ustreamer.tar.xz
cp -R /tmp/pikvm/usr/lib/ustreamer /usr/lib/

# Get python3-ustreamer package and extract it
wget -O python3-ustreamer.tar.gz https://github.com/ich777/pikvm-rockpi-s/raw/master/sourcepkgs/python3-ustreamer-5.37.tar.gz
tar -C /usr/lib/python3.11/ -xvf python3-ustreamer.tar.gz

# Grab overlay files for USB Host instead of OTG and enable UART2
wget -O /tmp/pikvm/rk3328-r8211f.dts https://github.com/ich777/pikvm-rockpi-e/raw/master/rk3328-overlays/rk3328-r8211f.dts
wget -O /tmp/pikvm/rk3328-uart1.dts https://github.com/ich777/pikvm-rockpi-e/raw/master/rk3328-overlays/rk3328-uart1.dts
wget -O /tmp/pikvm/rk3328-usb-host.dts https://github.com/ich777/pikvm-rockpi-e/raw/master/rk3328-overlays/rk3328-usb-host.dts
armbian-add-overlay /tmp/pikvm/rk3328-r8211f.dts
armbian-add-overlay /tmp/pikvm/rk3328-uart1.dts
armbian-add-overlay /tmp/pikvm/rk3328-usb-host.dts

# Grab systemd services, tempfiles.d and modified version from gpio.py for hid mcu
wget -O /etc/systemd/system/kvmd.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd.service
#wget -O /etc/systemd/system/kvmd-otg.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd-otg.service
wget -O /etc/systemd/system/kvmd-janus.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd-janus.service
wget -O /etc/systemd/system/kvmd-janus-static.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd-janus-static.service
wget -O /etc/systemd/system/kvmd-webterm.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd-webterm.service
wget -O /etc/systemd/system/kvmd-ipmi.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd-ipmi.service
wget -O /etc/systemd/system/kvmd-vnc.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd-vnc.service
wget -O /etc/systemd/system/kvmd-nginx.service https://github.com/ich777/pikvm-rockpi-s/raw/master/systemd/kvmd-nginx.service
wget -O /usr/lib/tmpfiles.d/kvmd.conf https://github.com/ich777/pikvm-rockpi-s/raw/master/tmpfiles.d/kvmd.conf
wget -O /usr/lib/python3.11/kvmd/plugins/hid/_mcu/gpio.py https://github.com/ich777/pikvm-rockpi-e/raw/master/mraa/hid/_mcu/gpio.py
wget -O /usr/lib/python3.11/kvmd/aiogp.py https://github.com/ich777/pikvm-rockpi-s/raw/master/mraa/aiogp.py

# Disable unnecessary services
systemctl disable kvmd-webterm kvmd-ipmi kvmd-vnc

# Get custom vcgencmd
wget -O /usr/bin/vcgencmd https://github.com/ich777/pikvm-rockpi-s/raw/master/vcgencmd
chmod +x /usr/bin/vcgencmd

# Get custom kvmd-udev-hdmiusb-check
wget -O /usr/bin/kvmd-udev-hdmiusb-check https://github.com/ich777/pikvm-rockpi-s/raw/master/bin/kvmd-udev-hdmiusb-check
chmod +x /usr/bin/kvmd-udev-hdmiusb-check

# Get udev rules and re-trigger
wget -O /etc/udev/rules.d/99-kvmd.rules https://github.com/ich777/pikvm-rockpi-e/raw/master/udev/99-kvmd.rules
udevadm control -R
udevadm trigger

# Generate certificates for nginx
openssl req -newkey rsa:4096 \
  -x509 \
  -sha256 \
  -days 3650 \
  -nodes \
  -out /etc/kvmd/nginx/ssl/server.crt \
  -keyout /etc/kvmd/nginx/ssl/server.key \
  -subj "/C=US/ST=New York/L=Brooklyn/O=PIKVM/CN=pikvm.org"

# Modify the nginx configuration files to be compatible with Debian 12 and enable nginx systemd service
sed -i '/http2 on/d' /etc/kvmd/nginx/listen-https.conf
mkdir -p /run/kvmd
mkdir -p /usr/share/tessdata
systemctl enable kvmd-nginx

# Patch export.py for Debian 12
sed -i 's/@async_lru.alru_cache(maxsize=1, ttl=5)/@async_lru.alru_cache()/g' /usr/lib/python3.11/kvmd/apps/kvmd/api/export.py

# Get main.yaml
wget -O /etc/kvmd/main.yaml https://github.com/ich777/pikvm-rockpi-s/raw/master/main.yaml

# Generate certificates for kvmd
openssl req -newkey rsa:4096 \
  -x509 \
  -sha256 \
  -days 3650 \
  -nodes \
  -out /etc/kvmd/vnc/ssl/server.crt \
  -keyout /etc/kvmd/vnc/ssl/server.key \
  -subj "/C=US/ST=New York/L=Brooklyn/O=PIKVM/CN=pikvm.org"

# Fix for ocr
rm -rf /usr/share/tessdata
ln -s /usr/share/tesseract-ocr/5/tessdata /usr/share/tessdata

# Patch override.yaml for this specific installation
printf "kvmd:\n    msd:\n        type: disabled\n    atx:\n        type: disabled\n    hid:\n        type: serial\n        device: /dev/ttyS1\n        reset_pin: 11\n        reset_inverted: true\n        reset_self: true\n        power_detect_pin: 7\n        power_detect_pull_down: true\n" >> /etc/kvmd/override.yaml

# Disable Power and Status LEDs on boot
sed -i '/^exit 0/i echo 0 > /sys/devices/platform/leds/leds/blue\\:/brightness\n' /etc/rc.local

# Adduser kvmd to satisfy services
adduser --disabled-password --gecos "" kvmd --disabled-login
```

### ATX (if you don't need ATX functionality skip the next part):

```
wget -O /usr/lib/python3.11/kvmd/plugins/atx/mraa.py https://github.com/ich777/pikvm-rockpi-e/raw/master/mraa/atx/mraa.py
sed -i '/atx:/,+1d' /etc/kvmd/override.yaml
echo -e "    atx:\n        type: mraa" >> /etc/kvmd/override.yaml
```

### WebTerminal (if you don't need WebTerminal functionality skip the next part):

```
mkdir -p /tmp/pikvm/webterm
cd /tmp/pikvm/webterm
wget -O pikvm-webterm.tar.xz https://github.com/ich777/pikvm-rockpi-s/raw/master/sourcepkgs/kvmd-webterm-0.48-1-any.pkg.tar.xz
tar -C /tmp/pikvm/webterm -xvf pikvm-webterm.tar.xz
cp -R /tmp/pikvm/webterm/usr/share/* /usr/share/
wget -O /usr/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.aarch64
chmod +x /usr/bin/ttyd

systemctl enable kvmd-webterm
```

### Endscript:

```
# Enable systemd services
#systemctl enable kvmd-otg
systemctl enable kvmd
systemctl enable kvmd-janus
systemctl enable kvmd-janus-static

# Reboot
reboot
```
