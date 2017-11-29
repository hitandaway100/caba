# -*- coding: utf-8 -*-
import random


def intCompress(n, base='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+!#$%&()=~|_?[]@:<>'):
    """10進数の値を圧縮.
    """
    t = base
    m = len(t)
    if n == 0: return t[0]
    r = []
    while 0 < n:
        r.append(t[n % m])
        n /= m
    return ''.join([i for i in reversed(r)])

def intDecompress(s, base='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+!#$%&()=~|_?[]@:<>'):
    """10進数の値を圧縮.
    """
    t = base
    m = len(t)
    d = 1
    ret = 0
    random.shuffle
    for i in xrange(len(s)):
        c = s[-(i+1)]
        v = t.index(c)
        ret += d * v
        d *= m
    return ret

def to62Decimal(n):
    """10進数の値を62進数に.
    """
    return intCompress(n, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
