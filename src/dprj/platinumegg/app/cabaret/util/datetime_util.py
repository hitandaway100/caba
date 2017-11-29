# -*- coding: utf-8 -*-
from defines import Defines
import datetime
from platinumegg.lib import timezone


class DateTimeUtil:
    
    @staticmethod
    def toLoginTime(now, hour=Defines.DATE_CHANGE_TIME):
        """現在時間を本日ログイン時間に変換.
        """
        return DateTimeUtil.toBaseTime(now, hour=hour)
    
    @staticmethod
    def toBaseTime(now, hour, minute=0, second=0):
        """現在時間を本日の日が変わる時間に変換.
        """
        diff = datetime.timedelta(hours=hour, minutes=minute, seconds=second)
        try:
            target = now-diff
        except OverflowError:
            # ここに来るのはdatetime.minだけのはずなのでちょっとずれてしまうけどとりあえず回避.
            target = now
        dt = datetime.datetime(target.year, target.month, target.day, hour, minute, second)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.TZ_DEFAULT)
        return dt
    
    @staticmethod
    def judgeSameDays(d1, d2):
        """同じ日付かをチェック.
        """
        l1 = DateTimeUtil.toLoginTime(d1)
        l2 = DateTimeUtil.toLoginTime(d2)
        delta = l1 - l2
        return 0 == delta.days
    
    @staticmethod
    def __get_admin_datetime_format():
        # 管理画面で使うdatetimeのフォーマット.
        return "%Y-%m-%d %H:%M:%S"
    @staticmethod
    def dateTimeToStr(dt):
        #datetimeを管理画面で表示する文字列に.
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.TZ_DB)
#        dt = dt.astimezone(OSAUtil.TZ_DEFAULT)
        dt = dt.astimezone(timezone.JST())
        return dt.strftime(DateTimeUtil.__get_admin_datetime_format())
    @staticmethod
    def strToDateTime(st, dtformat=None):
        #管理画面で入力された文字列をdatetimeに.
        #日本時間で入力されたものがくる想定.
        dtformat = dtformat or DateTimeUtil.__get_admin_datetime_format()
        return datetime.datetime.strptime(st, dtformat).replace(tzinfo=timezone.TZ_JST)
    
    @staticmethod
    def dateToDateTime(date):
        st = date.strftime(DateTimeUtil.__get_admin_datetime_format())
        return DateTimeUtil.strToDateTime(st)
    
    @staticmethod
    def datetimeToDate(dt, logintime=True):
        """datetimeをdateに.
        logintimeがTrueの時はログイン時間基準で.
        """
        if logintime:
            basetime = DateTimeUtil.toLoginTime(dt)
        else:
            basetime = DateTimeUtil.toBaseTime(dt, 0)
        return datetime.date(basetime.year, basetime.month, basetime.day)
