#!/usr/bin/env python3

# CH-jwt2json.py

# July 2021, <christian.tschudin@unibas.ch>
# see LICENSE for the copyright notice

import libs.chjwt as chjwt
import json
import sys

if len(sys.argv) != 4:
    print(f"usage: {sys.argv[0]} ROOT_CERT.crt UPDATES.jwt KEYLIST.jwt")
    sys.exit(-1)

root_cert = chjwt.load_x509_pem(sys.argv[1]) # trust anchor

updates = chjwt.load_jwt_str(sys.argv[2])
certs = chjwt.verify_and_dissect_jwt(updates, root_cert)['certs']

keylist = chjwt.load_jwt_str(sys.argv[3])
akids = chjwt.verify_and_dissect_jwt(keylist, root_cert)['activeKeyIds']

DCC_keys = {}
for c in certs: # different keys COULD have the same kid, hence an array
    DCC_keys[c['keyId']] = []
for c in certs:
    kid = c['keyId']
    if kid in akids: # only add active keys
        del c['keyId']
        del c['subjectPublicKeyInfo']
        DCC_keys[kid].append(c)

print(json.dumps(DCC_keys, indent=2))

# eof
