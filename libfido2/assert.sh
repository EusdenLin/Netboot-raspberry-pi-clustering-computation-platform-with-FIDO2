#! /bin/bash

echo assertion challenge | openssl sha256 -binary | base64 > cred_asset/assert_param
echo localhost >> cred_asset/assert_param
head -1 cred_asset/cred >> cred_asset/assert_param
tail -n +2 cred_asset/cred > cred_asset/pubkey
fido2-assert -G -i cred_asset/assert_param /dev/hidraw2 | fido2-assert -V cred_asset/pubkey es256
