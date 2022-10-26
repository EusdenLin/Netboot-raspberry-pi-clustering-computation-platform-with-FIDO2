#! /bin/bash

echo assertion challenge | openssl sha256 -binary | base64 > user/$1/assert_param
echo localhost >> user/$1/assert_param