## -*- coding: utf-8 -*-
import datetime
import json
import re
from platinumegg.lib import timezone

JSON_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
JSON_DATETIME_PTT = re.compile("[0-9].[0-9].-[0-9].-[0-9].\ [0-9].\:[0-9].\:[0-9]")

JSON_DATETIME_T_FORMAT = "%Y-%m-%dT%H:%M:%S"
JSON_DATETIME_T_PTT = re.compile("[0-9].[0-9].-[0-9].-[0-9].T[0-9].\:[0-9].\:[0-9]")

JSON_DATE_FORMAT = "%Y-%m-%d"
JSON_DATE_PTT = re.compile("[0-9].[0-9].-[0-9].-[0-9]")

class JsonDatetimeEncoder(json.JSONEncoder):
    """json.dumpsをする時に指定する.
    datetime型を指定フォーマットの文字列にするため.
    json_str = json.dumps(dict_data, cls=JsonDatetimeEncoder)
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(JSON_DATETIME_FORMAT)
        elif isinstance(obj, datetime.date):
            return obj.strftime(JSON_DATE_FORMAT)
        return json.JSONEncoder.default(self, obj)

def toDatetimeByJsonDatetimeStr(dct):
    """json.loadsをする時に指定する.
    datetimeっぽい文字列をdatetime型にするため.
    json.loads(json_str, object_hook=toDatetimeByJsonDatetimeStr)
    """
    # datetimeっぽいものをマッチさせようと思う.
    for k in dct.keys():
        if JSON_DATETIME_PTT.match("%s" % dct[k]):
            dct[k] = datetime.datetime.strptime(dct[k], JSON_DATETIME_FORMAT).replace(tzinfo=timezone.TZ_DEFAULT)
        elif JSON_DATETIME_T_PTT.match("%s" % dct[k]):
            dct[k] = datetime.datetime.strptime(dct[k], JSON_DATETIME_T_FORMAT).replace(tzinfo=timezone.TZ_DEFAULT)
        elif JSON_DATE_PTT.match("%s" % dct[k]):
            dt = datetime.datetime.strptime(dct[k], JSON_DATE_FORMAT).replace(tzinfo=timezone.TZ_DEFAULT)
            dct[k] = datetime.date(dt.year, dt.month, dt.day)
    return dct

class Json:
    @staticmethod
    def encode(obj, ensure_ascii=True):
        return json.dumps(obj, cls=JsonDatetimeEncoder, ensure_ascii=ensure_ascii)
    @staticmethod
    def decode(str_json):
        return json.loads(str_json, object_hook=toDatetimeByJsonDatetimeStr)

