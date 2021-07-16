#!/usr/bin/env python3

# CH-jwt2json.py

# July 2021, <christian.tschudin@unibas.ch>
# see LICENSE for the copyright notice


from base64 import b64decode, b64encode
import cryptography.x509 as x509
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from jose import jwk, jws, jwt
import json
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

# ---------------------------------------------------------------------------
if __name__ == '__main__':

    if len(sys.argv) != 4:
        print(f"usage: {sys.argv[0]} ROOT_CERT.crt UPDATES.jwt KEYLIST.jwt")
        sys.exit(-1)

    root_cert = load_x509_pem(sys.argv[1]) # trust anchor

    updates = load_jwt_str(sys.argv[2])
    certs = verify_and_dissect_jwt(updates, root_cert)['certs']

    keylist = load_jwt_str(sys.argv[3])
    akids = verify_and_dissect_jwt(keylist, root_cert)['activeKeyIds']
    
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
