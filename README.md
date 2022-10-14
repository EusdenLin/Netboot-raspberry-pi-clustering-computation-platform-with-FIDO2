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
