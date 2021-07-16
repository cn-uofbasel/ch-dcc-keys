#!/bin/bash

# CH-fetch_keys.sh

# usage: ./CH-fetch_keys.sh [tag]  (where tag is typically a date string)"

# July 2021, christian.tschudin@unibas.ch
# see LICENSE for the copyright notice



if [ "$#" == "0" ]; then
    TAG=`date -u +%Y%m%dat%H%M`
else
    TAG="$1"
fi

BASE_URL=https://www.cc.bit.admin.ch/trust/v1
DATA_DIR="./data"
ROOT_CRT="$DATA_DIR/CH-root.crt"
ROOT_URL="https://www.bit.admin.ch/dam/bit/en/dokumente/pki/scanning_center/swiss_governmentrootcaii.crt.download.crt/swiss_governmentrootcaii.crt"

if [ ! -f "$ROOT_CRT" ]; then
    curl -s -S $ROOT_URL >"$ROOT_CRT"
    if [ $? -ne 0 ]; then
        echo "** curl problem $? for $ROOT_CRT"
        exit
    fi
    echo "----> $ROOT_CRT"
else
    echo "using $ROOT_CRT"
fi

FN="$DATA_DIR/CH-$TAG-keylist.jwt"
curl -X GET -s -S \
     -H 'Accept: application/json+jws' \
     -H 'Accept-Encoding: gzip' \
     -H 'Authorization: Bearer 0795dc8b-d8d0-4313-abf2-510b12d50939' \
     -H 'User-Agent: ch.admin.bag.covidcertificate.wallet;2.1.1;1626211804080;Android;28' \
     $BASE_URL/keys/list   >$FN
if [ $? -ne 0 ]; then
    echo "** curl problem $? for keys/list"
    exit
fi
echo "----> $FN"

FN="$DATA_DIR/CH-$TAG-updates.jwt"
curl -X GET -s -S \
     -H 'Accept: application/json+jws' \
     -H 'Accept-Encoding: gzip' \
     -H 'Authorization: Bearer 0795dc8b-d8d0-4313-abf2-510b12d50939' \
     -H 'User-Agent: ch.admin.bag.covidcertificate.wallet;2.1.1;1626211804080;Android;28' \
     $BASE_URL/keys/updates?certFormat=ANDROID   >$FN
if [ $? -ne 0 ]; then
    echo "** curl problem $? for keys/updates"
    exit
fi
echo "----> $FN"

# eof
