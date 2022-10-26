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
1.  Install the following packages.
```
sudo su # It is much easier to follow the following commands if the user is root.
apt update
apt install -y nfs-kernel-server dnsmasq kpartx unzip
```

2. Download the latest Raspberry Pi OS and unzip it
```
wget -O raspbian_lite_latest.zip https://downloads.raspberrypi.org/raspbian_lite_latest
unzip raspbian_lite_latest.zip
```

3. Load raspbian filesystem by kpartx, then mount it.
```
kpartx -a -v *.img
mkdir bootmnt
mount rootmnt
mount /dev/mapper/loop0p1 bootmnt/ # if might not be loop0p1, you can find the correct partition from kpartx log
mount /dev/mapper/loop0p2 rootmnt/ 
```

4. Copy the filesystem to nfs-server and tftp server folder.
```
PI_SERIAL = ******** # the serial number from 'Raspberry Pi Setup' step 6.
KICKSTART_IP = xx.xx.xx.xx # the IP of dhcp server
mkdir -p /srv/nfs/rpi4-${PI_SERIAL}
mkdir -p /srv/tftpboot/${PI_SERIAL}
cp -a rootmnt/* /srv/nfs/rpi4-${PI_SERIAL}/
cp -a bootmnt/* /srv/nfs/rpi4-${PI_SERIAL}/boot/
```

5. Replace the default rPI firmware files with the latest version
```
rm /srv/nfs/rpi4-${PI_SERIAL}/boot/start4.elf
rm /srv/nfs/rpi4-${PI_SERIAL}/boot/fixup4.dat
wget https://github.com/Hexxeh/rpi-firmware/raw/stable/start4.elf -P /srv/nfs/rpi4-${PI_SERIAL}/boot/
wget https://github.com/Hexxeh/rpi-firmware/raw/stable/fixup4.dat -P /srv/nfs/rpi4-${PI_SERIAL}/boot/
```

6. Setup the NFS export and dnsmasq configuration
```
echo "/srv/nfs/rpi4-${PI_SERIAL}/boot /srv/tftpboot/${PI_SERIAL} none defaults,bind 0 0" >> /etc/fstab
echo "/srv/nfs/rpi4-${PI_SERIAL} *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports

cat > /etc/dnsmasq.conf << EOF
dhcp-range=xx.xx.xx.xx
log-dhcp
enable-tftp
tftp-root=/srv/tftpboot
pxe-service=0,"Raspberry Pi Boot"
EOF # You can either modify /etc/dnsmasq.conf here, remember the dhcp-range should be in the same subnet with dhcpserver.
mount /srv/tftpboot/${PI_SERIAL}/
```

7. Enable ssh to RPI, setup the nfs client info so that the nfs client can fetch its filesystem.
```
touch /srv/nfs/rpi4-${PI_SERIAL}/boot/ssh
sed -i /UUID/d /srv/nfs/rpi4-${PI_SERIAL}/etc/fstab
echo "console=serial0,115200 console=tty root=/dev/nfs nfsroot=${KICKSTART_IP}:/srv/nfs/rpi4-${PI_SERIAL},vers=3 rw ip=dhcp rootwait elevator=deadline" > /srv/nfs/rpi4-${PI_SERIAL}/boot/cmdline.txt
```

8. Enable and start the services
```
systemctl enable dnsmasq
systemctl enable rpcbind
systemctl enable nfs-server
systemctl start dnsmasq
systemctl start rpcbind
systemctl start nfs-server
```

9. Since I directly connect Raspberry Pi to my laptop through a cable. I need to define netmask and IP for my network interface.
```
ip addr add xx.xx.xx.xx/xx dev <if_name> # the KICKSTART_IP, netmask and your network interface name.
```

10. Now plug in power, cable. We are ready to boot RPI OS over network.

Trouble shoot:

* The IP of my interface disappear several times.

There might be some applications would reset your IP, you can check ```journalctl -xe``` to see what application did so. And disable the application.

The ideal way is separate the dhcp server and tftp server, the ip of your interface would be stable.

* Stuck at some init process...
Firstly you should make sure you followed the whole tutorial to netboot. You might lost some key firmware such as the latest start4.elf or fixup4.dat, so RPI cannot execute boot process properly.

* RPI doesn't find the dhcp server.
Please check systemctl status dnsmasq to see if your /etc/dnsmasq.conf runs properly.
Or run ```dnsmasq --test``` to see if there is syntax error in your configuration file or not.