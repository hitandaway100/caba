# -*- coding: utf-8 -*-

"""http://mitc.xrea.jp/diary/096
"""
import datetime

class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return datetime.timedelta(0)

class JST(datetime.tzinfo):
    def utcoffset(self,dt):
        return datetime.timedelta(hours=9)
    def dst(self,dt):
        return datetime.timedelta(0)
    def tzname(self,dt):
        return "JST"

TZ_DB = JST()
TZ_DEFAULT = JST()
TZ_UTC = UTC()
TZ_JST = JST()
