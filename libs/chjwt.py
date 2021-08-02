#!/usr/bin/env python3

# libs/chjwt.py

# July 2021, <christian.tschudin@unibas.ch>
# see LICENSE for the copyright notice

from base64 import b64decode, b64encode
import cryptography.x509 as x509
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from jose import jwk, jws, jwt
import math
import sys

def load_jwt_str(fn):
    with open(fn, 'r') as f:
        return f.read().strip()

def load_x509_pem(fn):
    with open(fn, 'rb') as f:
        return x509.load_pem_x509_certificate(f.read())

def verify_and_dissect_jwt(token, root_cert):

    def num2b64(x):
        sz = math.ceil(math.ceil(math.log(x,2)) / 8)
        return b64encode(x.to_bytes(sz, 'big')).decode()

    header = jws.get_unverified_header(token)

    lst = [b64decode(k) for k in header['x5c']]
    trustchain = [x509.load_der_x509_certificate(der) for der in lst]
    trustchain.append(root_cert)

    sha256WithRSAEncryption = x509.ObjectIdentifier('1.2.840.113549.1.1.11')
    padding = PKCS1v15()
    for i in range(len(trustchain)-1):
        signed, issuer = trustchain[i:i+2]
        if signed.signature_algorithm_oid != sha256WithRSAEncryption:
            raise Exception('not implemented: ' + \
                    str(signed.signature_algorithm_oid))
        # invalid signatur will raise an exception ...
        issuer.public_key().verify(signed.signature,
                signed.tbs_certificate_bytes,
                padding,
                signed.signature_hash_algorithm)

    pubnum = trustchain[0].public_key().public_numbers()
    sigkey = jwk.construct( {
        'kty': 'RSA',
        'alg': 'RS256',
        'n': num2b64(pubnum.n),
        'e': num2b64(pubnum.e)
        } )
    return jwt.decode(token, key=sigkey)

# eof
