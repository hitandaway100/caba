# coding: utf-8
import os
import glob

from django.db import connection
from django.db import connections
from django.core.management.base import BaseCommand

import settings
import settings_sub

from  platinumegg.app.cabaret.models.base.fields import ObjectField
from  platinumegg.app.cabaret.models import UserLog
import user_resettimes
from platinumegg.app.cabaret.models.UserLog import UserLogGacha
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

class Command(BaseCommand):
    """障害調査用.
    """
    def handle(self, *args, **options):
        self.stdout.write('Check table ...\n')
        cursor = connections[settings.DB_DEFAULT].cursor()
        self.stdout.write(
            '!!! MasterDB: {} !!!'.format(
                settings.DATABASES[cursor.db.alias]['HOST']
            )
        )
        self.stdout.write('start check seatgahca userdata ...\n')

#        dic = self._get_playcount(cursor)
#        self._get_gachaseatplaydata(cursor, dic)

        loguserdata = self._get_loguserdata(cursor)
        resettimes = user_resettimes.user_resettimes
        count = 0
        flag = False
        prizecount = 0
        usercount = {}
        
        self.stdout.write('playerid, count')
        for uid, datelist in resettimes.items():
            if not loguserdata.get(uid):
                # そもそももらってない.
                continue
            # 時間をくっつけちゃう.
            arr = list(set(datelist + loguserdata[uid]))
            # ソート.
            arr.sort()
            flag = False
            prizecount = 0
            for d in arr:
                if d in datelist:
                    # ここリセット.
                    # ここで配布確定.
                    if flag:
                        prizecount += 1
                    flag = False
                if d in loguserdata[uid]:
                    # ここチケット獲得.
                    # ここに来ただけでは配布未確定
                    flag = True
            if prizecount:
                self.stdout.write('{}, {}'.format(uid, prizecount*2))
                
#         for uid, datelist in resettimes.items():
#             for resettime in datelist:
#                 if loguserdata.get(uid):
#                     for presenttime in loguserdata.get(uid):
#                         if resettime < presenttime:
#                             flag = True
#                             if 0 == count:
#                                 prizecount += 1
#                             break
#                         count += 1
#                         if 3 <= count:
#                             flag = True
#                             break
#                 if flag:
#                     loguserdata[uid] = loguserdata[uid][count+1:]
#                     count = 0
#                     if prizecount:
#                         usercount[uid] = prizecount
#                     flag = False
#             prizecount = 0
#         self.stdout.write('playerid, count')
#         for uid, count in usercount.items():
#             if 0 < count:
#                 self.stdout.write('{}, {}'.format(uid, count))

    def _get_playcount(self, cursor):
        try:
            cursor.execute("select uid, lap from cabaret_gachaseattableplaycount where mid=23;")
            row = cursor.fetchall()
        except:
            pass
        lapdata = row
        dic = {}
        for uid, lap in lapdata:
            if dic.get(uid):
                dic[uid] += lap*2
            else:
                dic[uid] = lap*2
        return dic

    def _get_gachaseatplaydata(self, cursor, dic):
        try:
            cursor.execute("select uid, flag_2 from cabaret_gachaseatplaydata where mid=41 or mid=42;")
            row = cursor.fetchall()
        except:
            pass

        flagdata = row
        for uid, flag in flagdata:
            if dic.get(uid):
                dic[uid] += flag*2
            else:
                dic[uid] = flag*2

    def _get_loguserdata(self, cursor):
#         try:
#             cursor.execute("select uid, ctime, data from cabaret_userloggacha where '2015-09-29'<ctime and ctime<'2015-10-02 14:00:00';")
#             row = cursor.fetchall()
#         except:
#             pass
        filters = dict(ctime__gt=DateTimeUtil.strToDateTime('2015-09-29', '%Y-%m-%d'), ctime__lt=DateTimeUtil.strToDateTime('2015-10-02 14:00:00', '%Y-%m-%d %H:%M:%S'))
        loguserdata = {}
#         for uid, ctime, log in row:
        for model in UserLogGacha.fetchValues(filters=filters):
            uid, ctime, logdata = model.uid, model.ctime, model.data
#             obj = ObjectField()
#             logdata = obj.to_python(log)
            mid = logdata.get('mid')
            prizeid = logdata.get('seat_prizeid')
            if prizeid == 600301 and mid == 1086:
                if loguserdata.get(uid):
                    loguserdata[uid].append(ctime.replace(tzinfo=None))
                else:
                    loguserdata[uid] = [ctime.replace(tzinfo=None)]

        for v in loguserdata.values():
            v.sort()
        return loguserdata
