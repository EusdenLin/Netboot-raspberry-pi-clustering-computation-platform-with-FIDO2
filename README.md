# Netboot-raspberry-pi-clustering-computation-platform-with-FIDO2

## System spec
* OS: Ubuntu 20.04
* CPU: intel i7-8550U 
* RAM: 16GB


## Flashing the firmware to makerdiary nrf52840 usb mdk dongle

### Way 1. Build a firmware from google/OpenSK 

> using submodule-google/OpenSK

I followed the steps on google/OpenSK to build the u2f file for security key.

#### gerneral steps:
> Make sure your environment fulfilled the requirements of OpenSK
1. Clone the repo from https://github.com/google/OpenSK
2. Run ```./setup.sh```
3. Install a udev rule to allow non-root user to interact with OpenSK devices.
```
sudo cp rules.d/55-opensk.rules /etc/udev/rules.d/
sudo udevadm control --reload
```

#### Build and flash firmware to OpenSK device
1. Build the hex file with firmware:
```
./deploy.py --board=nrf52840_mdk_dfu --opensk --programmer=none 
```

2. Download the script from Makerdiary's GitHub into the OpenSK repository.
```
wget https://raw.githubusercontent.com/makerdiary/nrf52840-mdk-usb-dongle/master/tools/uf2conv.py
```

3. Then run the script with following arguments:
```
python3 uf2conv.py -c -f 0xada52840 -o target/opensk.uf2 target/nrf52840_mdk_dfu_merged.hex
```

4. Boot into DFU mode. Keep the user button pressed on your hardware while inserting it into a USB slot. You should see a bit of red blinking, and then a constant green light.

5. Your dongle should appear in your normal file browser like other USB sticks. Copy the file target/opensk.uf2 over.

6. Replug to reboot.

### Way 2. using firmware from makerdiary repo

> Though you don't need to build a firmware through OpenSK, this version of firmware doesn't support libfido2.

1. Download the u2f file from makerdiary/nrf52840-mdk-usb-dongle repo
```
wget https://github.com/makerdiary/nrf52840-mdk-usb-dongle/raw/master/firmware/OpenSK/opensk_nrf52840_mdk_usb_dongle_gece14d7.uf2
```
2. Boot into DFU mode. Keep the user button pressed on your hardware while inserting it into a USB slot. You should see a bit of red blinking, and then a constant green light.

3. Your dongle should appear in your normal file browser like other USB sticks. Copy the file target/opensk.uf2 over.

4. Replug to reboot.

### Demo
webauthn.io is a website for you to verify whether your security keys are flashed successfully or not.

Otherwise, you can use this security key to login to your google account. (warning: if you only got one security key, I highly recommend you to test it on an unimaportant account.)

## An easy website for FIDO2 authentication

> I used py_webauthn and Flask to setup the authentication website.

Running the commands below to setup the flask server:
```
cd ./py_webauthn
flask run --host=0.0.0.0 
```

After that, you can open your browser and browse ```http://localhost:5000```.

When you get into the page, you can either register or login to this website. Though I didn't make a database for this website, this server can only remember on user at once, that is as long as a new user is register , the old one cannot login anymore.

## PXE boot Raspberry Pi

> I followed [this page](https://williamlam.com/2020/07/two-methods-to-network-boot-raspberry-pi-4.html) to setup the eeprom of Raspberry Pi and dnsmasq, dns servers.  

### Raspberry Pi spec

RAM: 8GB
model: 4b

### Raspberry Pi Setup
1. Download and install the Raspberry Pi Imager Tool for your OS.
2. Flash your SD card with the imager tool, I choosed Raspbian OS Lite(latest version) as the system I want to boot RPI.
3. You can either enable SSH access through imager tool(while flashing OS to the sd card), or you can enable SSH by running the following commands:
```
systemctl start ssh
```
4. Upgrade and update apt.
```
sudo apt update
sudo apt full-upgrade
```
5. Download and apply the RPI eeprom which supports network booting. Also change the boot order. 
```
PI_EEPROM_VERSION=pieeprom-2020-06-15
wget https://github.com/raspberrypi/rpi-eeprom/raw/master/firmware/beta/${PI_EEPROM_VERSION}.bin
sudo rpi-eeprom-config ${PI_EEPROM_VERSION}.bin > bootconf.txt
sed -i 's/BOOT_ORDER=.*/BOOT_ORDER=0xf241/g' bootconf.txt
sudo rpi-eeprom-config --out ${PI_EEPROM_VERSION}-netboot.bin --config bootconf.txt ${PI_EEPROM_VERSION}.bin
sudo rpi-eeprom-update -d -f ./${PI_EEPROM_VERSION}-netboot.bin
```
6. Retrieve your Raspberry Pi serial number and MAC address, they will be used.
```
cat /proc/cpuinfo | grep Serial | awk -F ': ' '{print $2}' | tail -c 8 # your RPI serial number
ip addr show eth0 | grep ether | awk '{print $2}' # your MAC Address
```
Then you can shutdown and remove SD card from your Raspberry PI.

### Setup DHCP, TFTP, NFS server
