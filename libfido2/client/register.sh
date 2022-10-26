#! /bin/bash

rm pubkey cred_param assert_param cred

curl -X POST 127.0.0.1:5000/register_request -F "Username=$1" > cred_param
echo =============================================
echo = Please Touch The Button On Your Device... =
echo =============================================


fido2-cred -M -i cred_param /dev/hidraw2 | fido2-cred -V -o cred
