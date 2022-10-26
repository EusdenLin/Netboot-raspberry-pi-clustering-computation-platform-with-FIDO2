#! /bin/bash

echo credential challenge | openssl sha256 -binary | base64 > user/$1/cred_param
echo localhost >> user/$1/cred_param
echo $1 >> user/$1/cred_param
dd if=/dev/urandom bs=1 count=32 | base64 >> user/$1/cred_param


