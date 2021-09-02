#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Decrypt and encrypt messages compatible to the "Stanford Javascript Crypto
Library (SJCL)" message format.
"""

import base64

from Crypto.Hash import SHA256, HMAC
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES


def truncate_iv(iv, ol, tlen):
    ivl = len(iv)
    ol = (ol - tlen) // 8

    L = 2
    while (L < 4) and ((ol >> (8 * L))) > 0:
        L += 1
    if L < 15 - ivl:
        L = 15 - ivl

    return iv[: (15 - L)]


def fix_padding(value: str) -> str:
    if len(value) % 4:
        return value + ("=" * (4 - len(value) % 4))
    return value


def get_aes_mode(mode: str):
    """Return pycrypto's AES mode, raise exception if not supported"""
    aes_mode_attr = "MODE_{}".format(mode.upper())
    try:
        aes_mode = getattr(AES, aes_mode_attr)
    except AttributeError:
        raise Exception(
            "Pycrypto/pycryptodome does not seem to support {}. ".format(aes_mode_attr)
            + "If you use pycrypto, you need a version >= 2.7a1 (or a special branch)."
        )
    return aes_mode


class SJCL(object):
    def __init__(self):
        self.salt_size = 8  # bytes
        self.prf = lambda passphrase, salt: HMAC.new(passphrase, salt, SHA256).digest()

    def decrypt(self, data: dict, passphrase: str):
        if data["cipher"] != "aes":
            raise Exception("only aes cipher supported")

        aes_mode = get_aes_mode(data["mode"])
        tlen = data["ts"]

        if data["adata"] != "":
            raise Exception("additional authentication data not equal ''")

        if data["v"] != 1:
            raise Exception("only version 1 is currently supported")

        if aes_mode == AES.MODE_CCM:
            data["salt"] = fix_padding(data["salt"])

        salt = base64.b64decode(data["salt"])
        if len(salt) != self.salt_size:
            raise Exception("salt should be %d bytes long" % self.salt_size)

        dkLen = data["ks"] // 8
        if dkLen != 16 and dkLen != 32:
            raise Exception("key length should be 16 bytes or 32 bytes")

        key = PBKDF2(passphrase, salt, count=data["iter"], dkLen=dkLen, prf=self.prf)
        if aes_mode == AES.MODE_CCM:
            data["iv"] = fix_padding(data["iv"])
            data["ct"] = fix_padding(data["ct"])

        ciphertext = base64.b64decode(data["ct"])
        iv = base64.b64decode(data["iv"])

        nonce = iv
        if aes_mode == AES.MODE_CCM:
            nonce = truncate_iv(iv, len(ciphertext) * 8, data["ts"])

        mac = ciphertext[-(data["ts"] // 8) :]
        ciphertext = ciphertext[: -(data["ts"] // 8)]

        cipher = AES.new(key, aes_mode, nonce, mac_len=tlen // 8)
        plaintext = cipher.decrypt(ciphertext)

        cipher.verify(mac)

        return plaintext
