# -*- coding: utf-8 -*-
import time
import sys
from django.core import exceptions
from sqlalchemy.exc import TimeoutError
from _mysql_exceptions import OperationalError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError


def comma_validate(value):
    # カンマ区切りか確認.
    
    try:
        value.split(',')
    except:
        err_tex = u'カンマ区切りのデータで入力して下さい。data=%s' % value
        raise exceptions.ValidationError(err_tex)

def comma_int_validate(value):
    # カンマ区切りの数値か確認.
    comma_validate(value)
    try:
        for v in value.split(','):
            if v:
                int(v)
    except ValueError:
        err_tex = u'数値じゃないものが含まれています。data=%s' % value
        raise exceptions.ValidationError(err_tex)

def float_validate(value):
    # floatか確認.
    
    try:
        float(value)
    except:
        err_tex = u'float型で入力して下さい。data=%s' % value
        raise exceptions.ValidationError(err_tex)

def save_custom_retries(method, *args, **kwargs):
    """書き込みﾘﾄﾗｲﾒｿｯﾄﾞ.
    トランザクションをはっていないときに呼ばれる.
    """
    start_time = OSAUtil.get_now()
    while True:
        try:
            return method(*args, **kwargs)
        except TimeoutError:
            # db接続ﾀｲﾑｱｳﾄ.
            raise
        except OperationalError:
            # mysqlの接続等のエラー.
            now = OSAUtil.get_now()
            dif = now - start_time
            if dif.seconds < 3:
                time.sleep(0.1)
            else:
                info = sys.exc_info()
                trace = CabaretError.makeErrorTraceString(info)
                raise CabaretError(trace, CabaretError.Code.TOO_MANY_TRANSACTION)



def get_pointprizes(pointprizes, point_min=1, point_max=None):
    if point_max is None:
        filter_func = lambda x:point_min <= x
    else:
        filter_func = lambda x:point_min <= x <= point_max
    
    def countfilter(table):
        keys = table.keys()
        for key in keys:
            if not filter_func(key):
                del table[key]
        return table
    
    if isinstance(pointprizes, list):
        return countfilter(dict(pointprizes))
    elif not isinstance(pointprizes, dict):
        return {}
    
    table = countfilter(dict(pointprizes.get('normal') or []))
    repeat = pointprizes.get('repeat') or []
    
    for data in repeat:
        prize = data.get('prize')
        if not prize:
            continue
        
        d_min = max(1, data.get('min', 1))
        if point_max is None:
            d_max = d_min
        else:
            d_max = min(data.get('max', point_max), point_max)
        interval = max(1, data.get('interval', 1))
        
        d = d_min + int((point_min - d_min + interval - 1) / interval) * interval
        while d <= d_max:
            arr = table[d] = table.get(d) or []
            arr.extend(prize)
            d += interval
    return table

def dict_to_choices(dict_obj):
    """辞書型のデータをプルダウンのパラメータに変換.
    """
    return [(k,'%s:%s' % (k,v)) for k,v in dict_obj.items()]
