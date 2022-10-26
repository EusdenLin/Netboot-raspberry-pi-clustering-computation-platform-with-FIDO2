#! /bin/bash

echo credential challenge | openssl sha256 -binary | base64 > cred_asset/cred_param
echo localhost >> cred_asset/cred_param
echo eusden >> cred_asset/cred_param
dd if=/dev/urandom bs=1 count=32 | base64 >> cred_asset/cred_param
fido2-cred -M -i cred_asset/cred_param /dev/hidraw2 | fido2-cred -V -o cred_asset/cred

