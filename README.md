# ```ch-dcc-keys```: DCC Signing Keys and the Swiss Trust Chain

This repo is about fetching the Europe-wide list of _"Digital COVID
Certificate signing keys"_ (DCC keys) as served by the Swiss
Government. Our tool assesses the trustworthiness of these keys by
checking the Swiss Government's digital signature chain that is
attached to the returned data.

# Quick Start

```text
% ./CH-fetch_keys.sh
----> ./data/CH-root.crt
----> ./data/CH-20210715at1944-keylist.jwt
----> ./data/CH-20210715at1944-updates.jwt
% ./CH-jwt2json.py data/CH-root.crt \
                   data/CH-20210715at1944-updates.jwt \
                   data/CH-20210715at1944-keylist.jwt \
                 > data/CH-20210715at1944-DCCkeys.json
```
The file of interest, in this case, is ```data/CH-20210715at1944-DCCkeys.json```


# Background on the Swiss "List of DCC keys" Setup

The BIT (Bundesamt für Informatik und Telekommunikation) has two REST
endpoints at ```https://www.cc.bit.admin.ch/trust/v1```
where (a) a list of DCC key parameters, and (b) a table of
active key IDs can be fetched. Both calls seem to need a bearer token which
we extracted from the BIT's Android CovidCertificate app. As of July
15, 2021, the token is:

```text
Authorization: Bearer 0795dc8b-d8d0-4313-abf2-510b12d50939
```

Although we don't make use of the SDK (and therefore are not bound by
the following) and believe that access to governmental public keys
should be permissionless, we point to the comment in the Android app's
source code:
```
// If you intend to integrate the CovidCertificate-SDK into your app,
// please get in touch with BIT/BAG to get a token assigned.
```
See https://github.com/admin-ch/CovidCertificate-SDK-Android/ from where
we grabbed the bearer token value from the gradle file.


## keys/list

The ```keys/list``` endpoint returns a JSON Web Token. The JWT
includes a trustchain that can be verified if one adds the Swiss
Government's self-signed root certificate "CA II" as a trust anchor.

Unlike what the endpoint's name suggests, the token's payload contains
a list of "activeKeyIds", _not_ the keys themselves. It is our
understanding that this list is a way to implement key revocation
checks: the BIT signs off this list in order to assert that these keys
have not been revoked. Nice service!


## keys/updates

The ```keys/updates``` endpoint also returns a JSON Web Token,
including a trustchain as for the ```keys/list``` token, and
is the "real" DCC key database.

The payload of the ```updates``` token is a list of DCC keys for which
all essential cryptographic details are provided (see the JSON output
below). The list is called ```certs``` although is contains the naked
parameters without further signature bits: One has thus to trust
BIT to have extracted the correct values (or compare with the keys
obtained from other countries...).


## A Note on the CH Trust Anchor (for the paranoid among us)

The ```CH-fetch_keys.sh``` script fetches the Swiss Government's
root certificate "CA II" via URL, once. In each subsequent run it will reuse
the file that was fetched (```./data/CH-root.crt```), resulting in
pinning this certificate.

So you better check that the first download of that certificate is
what you want to have as a trust anchor.  If you blindly execute the
script this means that you trust the Web's Public Key Infrastructure
and its agents having set up the Web server correctly and serving you
the right bits. In doubt, inspect the downloaded root certificate and
compare with alternate sources e.g.,
```https://github.com/admin-ch/CovidCertificate-SDK-Android/blob/main/sdk/src/main/assets/swiss_governmentrootcaii.der```

There is an old story (running joke?) about the Swiss Government
trying to get that root certificate inside Mozilla's CA bundle, since
2008 ... see https://bugzilla.mozilla.org/show_bug.cgi?id=435026 . As
of July 2021 it is still open. If that issue would have been dealt
with you could trust the SwissRootCAII entry that would come with Firefox (if
you trust Mozilla), but hélas!

Governmental root certificates are a sensitive topic. See e.g. Kazakhstan's
repeated attempts to force dubious certs upon its citizens for spying purposes
https://www.zdnet.com/article/kazakhstan-government-is-intercepting-https-traffic-in-its-capital/ (Dec 2020)


# JSON Output

The ```CH-jwt2json.py``` script works fully offline. It expects three
parameters:
- ```root cert``` filename (PEM format)
- ```updates``` filename (JWT)
- ```keylist``` filename (JWT)

and does the following:
- extract for each of the JWT files the trust chain
- add the Swiss CAII root certificate to these chains and verify the chains
- verify the signature of both JWTs
- extract ```activeKeyIds``` and ```certs``` from the two JWT files
- build a dictionary indexed by keyId
- only add keys (from ```certs```) if their keyId is in ```activeKeyIds```
- for each keyId entry we have an array of keys (as a keyId could match
  several keys, although this is unlikely)

The output of the Python script is in JSON format where we show the
first few lines:

```
{
  "Ll3NP03zOxY=": [
    {
      "use": "sig",
      "alg": "RS256",
      "n": "ALZP+dbLSV1OPEag9pYeCHbMRa45SX5kwqy693EDRF5KxKCNzhFfDZ6LRNUY1ZkK6i009OKMaVpXGzKJV7SQbbt6zoizcEL8lRG4/8UnOik/OE6exgaNT/5JLp2PlZmm+h1Alf6BmWJrHYlD/zp0z1+lsunXpQ4Z64ByA7Yu9/00rBu2ZdVepJu/iiJIwJFQhA5JFA+7n33eBvhgWdAfRdSjk9CHBUDbw5tM5UTlaBhZZj0vA1payx7iHTGwdvNbog43DfpDVLe61Mso+kxYF/VgoBAf+ZkATEWmlytc3g02jZJgtkuyFsYTELDAVycgHWw/QJ0DmXOl0YwWrju4M9M=",
      "e": "AQAB",
      "crv": null,
      "x": null,
      "y": null
    }
  ],
  "e/YRqyv++qY=": [
    {
      "use": "sig",
      "alg": "ES256",
      "n": null,
      "e": null,
      "crv": "P-256",
      "x": "mCCGUDO95y6Rj40KX74cFgc99I9BnFoPBkZ3kcAyo2o=",
      "y": "v7JjeIG2FpKwtljBK7DfM2d+wvUYQBpR2AzfLTyW4gM="
    }
  ],
  ...
```

---
