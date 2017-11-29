# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseMaster, Singleton
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    PositiveBigIntegerField, AppDateTimeField, ObjectField
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from defines import Defines
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class LoginBonusMaster(BaseMaster):
    """連続ログインボーナス.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    day = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'日数')
    thumb = models.CharField(max_length=48, verbose_name=u'サムネイル')
    prizes = JsonCharField(default=list, verbose_name=u'報酬')

class AccessBonusMaster(BaseMaster):
    """アクセス日数ボーナス.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    day = models.PositiveSmallIntegerField(primary_key=True, verbose_name=u'日数(0は毎日)')
    thumb = models.CharField(max_length=48, verbose_name=u'サムネイル')
    prizes = JsonCharField(default=list, verbose_name=u'報酬')

class TotalLoginBonusConfig(Singleton):
    """累計ログインボーナスの設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveIntegerField(default=0, verbose_name=u'マスターID')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間')
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間')
    mid_next = models.PositiveIntegerField(default=0, verbose_name=u'次のマスターID')
    continuity_login = models.BooleanField(default=True, verbose_name=u'連続ログイン公開フラグ')
    
    def getCurrentMasterID(self, now=None):
        now = now or OSAUtil.get_now()
        if self.stime <= now < self.etime:
            return self.mid
        elif self.etime <= now:
            return self.mid_next
        else:
            return 0

class LoginBonusTimeLimitedConfig(Singleton):
    """期限付きログインボーナスの設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    mid = models.PositiveIntegerField(default=0, verbose_name=u'マスターID(廃止予定)')
    stime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間(廃止予定)')
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間(廃止予定)')
    datalist = JsonCharField(default=list, verbose_name=u'設定内容')
    
    def __reflesh(self):
        if not self.datalist:
            self.datalist = []
        
        if self.mid:
            datadict = dict(self.datalist)
            if datadict.get(self.mid) is None:
                self.__setData(self.mid, self.stime, self.etime, idx=0, sugoroku=False)
            self.mid = 0
    
    def formatData(self):
        self.mid = 0
        self.datalist = []
    
    def setData(self, mid, stime, etime, idx=None, beginer=False, sugoroku=False):
        self.__reflesh()
        self.__setData(mid, stime, etime, idx, beginer=beginer, sugoroku=sugoroku)
    
    def __setData(self, mid, stime, etime, idx=None, beginer=False, sugoroku=False):
        data = (mid, {'mid':mid,'stime':stime,'etime':etime,'beginer':beginer,'sugoroku':sugoroku})
        if idx is None:
            datadict = dict(self.datalist)
            # 順番を未指定.
            if datadict.has_key(mid):
                # 既存のものを上書き.
                datadict[mid].update(data[1])
            else:
                # 無いので新規.
                self.datalist.append(data)
        else:
            # 場所を指定.
            arr = []
            flag = False
            for _data in self.datalist:
                if len(arr) == idx:
                    arr.append(data)
                    flag = True
                if _data[0] == mid:
                    pass
                else:
                    arr.append(_data)
            if not flag:
                arr.append(data)
            self.datalist = arr
    
    def getData(self, idx=0):
        self.__reflesh()
        if idx < len(self.datalist):
            return self.datalist[idx][1]
        else:
            return None
    
    def getDataList(self):
        self.__reflesh()
        return self.datalist

class LoginBonusTimeLimitedMaster(BaseMaster):
    """期限付きログインボーナスの設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    htmlname = models.CharField(max_length=64, verbose_name=u'HTML名(ロングログイン)')
    effectname = models.CharField(max_length=64, verbose_name=u'演出名(ロングログイン)')
    textid = models.PositiveIntegerField(default=0, verbose_name=u'報酬テキストID(ロングログイン)')
    lbtype = models.PositiveSmallIntegerField(default=Defines.LoginBonusTimeLimitedType.TOTAL, verbose_name=u'日付固定フラグ', choices=dict_to_choices(Defines.LoginBonusTimeLimitedType.NAMES))
    # 演出用パラメータ.
    logo = models.BooleanField(default=False, verbose_name=u'ロゴの有無')
    img_effect = models.CharField(max_length=96, verbose_name=u'演出画像', blank=True)
    text_logo = models.CharField(max_length=128, verbose_name=u'演出文言(ロゴ表示時)', blank=True)
    text_start = models.CharField(max_length=128, verbose_name=u'演出文言(開始)', blank=True)
    text_itemlist = models.CharField(max_length=128, verbose_name=u'演出文言(報酬一覧)', blank=True)
    text_itemget = models.CharField(max_length=128, verbose_name=u'演出文言(アイテム獲得)', blank=True)
    text_itemnext = models.CharField(max_length=128, verbose_name=u'演出文言(明日のアイテム)', blank=True)
    text_end = models.CharField(max_length=128, verbose_name=u'演出文言(終了,タッチ待ち)', blank=True)

class LoginBonusTimeLimitedDaysMaster(BaseMaster):
    """期限付きログインボーナス.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    mid = models.PositiveIntegerField(verbose_name=u'マスターID')
    day = models.PositiveSmallIntegerField(verbose_name=u'日数')
    thumb = models.CharField(default='', max_length=128, verbose_name=u'サムネイル')
    prizes = JsonCharField(default=list, verbose_name=u'報酬')
    
    # 演出用パラメータ.
    bg = models.CharField(max_length=96, verbose_name=u'背景画像', blank=True)
    text_logo = models.CharField(max_length=128, verbose_name=u'演出文言(ロゴ表示時)', blank=True)
    text_start = models.CharField(max_length=128, verbose_name=u'演出文言(開始)', blank=True)
    text_itemlist = models.CharField(max_length=128, verbose_name=u'演出文言(報酬一覧)', blank=True)
    text_itemget = models.CharField(max_length=128, verbose_name=u'演出文言(アイテム獲得)', blank=True)
    text_itemnext = models.CharField(max_length=128, verbose_name=u'演出文言(明日のアイテム)', blank=True)
    text_end = models.CharField(max_length=128, verbose_name=u'演出文言(終了,タッチ待ち)', blank=True)
    
    item_x = models.PositiveSmallIntegerField(verbose_name=u'アイテムの表示位置(x)', default=80)
    item_y = models.PositiveSmallIntegerField(verbose_name=u'アイテムの表示位置(y)', default=200)
    
    @staticmethod
    def makeID(mid, day):
        return (mid << 32) + day
    
    @classmethod
    def makeInstance(cls, key):
        model = cls()
        model.id = key
        model.mid = int(key >> 32)
        model.day = int(key & 0xffffffff)
        return model

class LoginBonusTimeLimitedData(BasePerPlayerBaseWithMasterID):
    """期限付きログインボーナスの受け取り情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    days = models.PositiveSmallIntegerField(default=0, verbose_name=u'プレイ日数')
    lbtltime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'受取り時間')

class LoginBonusSugorokuMaster(BaseMaster):
    """すごろくログインボーナス.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    maps = JsonCharField(default=list, verbose_name=u'使用するマップID')
    
    def getMapIDByLap(self, lap):
        return self.maps[lap % len(self.maps)]

class LoginBonusSugorokuMapMaster(BaseMaster):
    """すごろくログインボーナスのマップ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    effectname = models.CharField(max_length=64, verbose_name=u'演出名')
    prize = JsonCharField(default=list, verbose_name=u'達成済み報酬')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'達成済み報酬テキストID')

class LoginBonusSugorokuMapSquaresMaster(BaseMaster):
    """すごろくログインボーナスのマップのマス.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'マップID')
    number = models.PositiveIntegerField(verbose_name=u'マップ内マス番号')
    name = models.CharField(max_length=48, verbose_name=u'名前(表示用)')
    name_mgr = models.CharField(max_length=48, verbose_name=u'名前(管理用)')
    thumb = models.CharField(default='', max_length=128, verbose_name=u'画像')
    event_type = models.PositiveSmallIntegerField(default=Defines.SugorokuMapEventType.NONE, choices=Defines.SugorokuMapEventType.NAMES.items(), verbose_name=u'発生するイベントの種別')
    event_value = models.PositiveIntegerField(default=0, verbose_name=u'発生するイベントの値', help_text=u'event_typeにあわせて用途が変化。進むor戻る→移動量, 休み→休む回数, 飛ぶ→飛び先のマス番号')
    prize = JsonCharField(default=list, verbose_name=u'停まった時の報酬')
    prize_text = models.PositiveIntegerField(default=0, verbose_name=u'停まった時の報酬テキストID')
    last = models.BooleanField(default=False, verbose_name=u'最終マスフラグ')
    
    @staticmethod
    def makeID(mid, number):
        return (mid << 32) + number
    
    @classmethod
    def makeInstance(cls, key):
        model = cls()
        model.id = key
        model.mid = int(key >> 32)
        model.number = int(key & 0xffffffff)
        return model

class LoginBonusSugorokuPlayerData(BasePerPlayerBaseWithMasterID):
    """ユーザーのすごろくログインボーナス情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    ltime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'受取り時間')
    lap = models.PositiveIntegerField(default=0, verbose_name=u'周回数')
    loc = models.PositiveIntegerField(default=1, verbose_name=u'現在のマス')
    lose_turns = models.PositiveIntegerField(default=0, verbose_name=u'残り休み回数')
    result = ObjectField(default=dict, verbose_name=u'演出用の結果保持')
    
    def setResult(self, number, square_id_list):
        self.result = dict(
            number = number,    # 出た目.
            square_id_list = square_id_list,    # 開始位置を含む、停まったマスのIDのリスト.
        )

