#! /bin/bash

curl -X POST 127.0.0.1:5000/login_request -F "Username=$1" > assert_param

head -1 cred >> assert_param
tail -n +2 cred > pubkey

echo =============================================
echo = Please Touch The Button On Your Device... =
echo =============================================

fido2-assert -G -i assert_param /dev/hidraw2 | fido2-assert -V pubkey es256