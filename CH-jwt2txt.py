#!/usr/bin/env python3

# CH-jwt2txt.py

# July 2021 <christian.tschudin@unibas.ch>
# see LICENSE for the copyright notice

import libs.chjwt as chjwt
import sys

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print(f"usage with jwt file: {sys.argv[0]} ROOT_CERT.crt response.jwt")
    print(f"usage with jwt on stdin: {sys.argv[0]} ROOT_CERT.crt")
    sys.exit(-1)

root_cert = chjwt.load_x509_pem(sys.argv[1]) # trust anchor

jwtfile = ''
if len(sys.argv) == 3:
    jwtfile = chjwt.load_jwt_str(sys.argv[2])
else:
    jwtfile = chjwt.load_jwt_str('/dev/stdin')

res = chjwt.verify_and_dissect_jwt(jwtfile, root_cert)['revokedCerts']

for r in res:
    print(r)
