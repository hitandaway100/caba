# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from platinumegg.app.cabaret.models.base.models import BaseModel,\
    BaseMasterWithThumbnail, BaseMaster
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.base.fields import JsonCharField,\
    AppDateTimeField, ObjectField, PositiveBigIntegerField
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines

class CabaClubMaster(BaseMaster):
    """キャバクラシステムの設定.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    week = models.PositiveIntegerField(default=0, unique=True, verbose_name=u'年と週', help_text=u'2015年5週目は201505,2015年10週目は201510')
    name = models.CharField(max_length=48, verbose_name=u'名前')
    customer_prizes = JsonCharField(default=list, verbose_name=u'集客数達成報酬', help_text=u'[[報酬ID,出現率(1-10000)],...]')
    customer_prize_text = models.PositiveIntegerField(default=0, verbose_name=u'集客数達成報酬文言ID')
    customer_prize_interval = models.PositiveIntegerField(default=0, verbose_name=u'集客数報酬獲得抽選の間隔')
    cr_correction = JsonCharField(default=dict, verbose_name=u'キャストレアリティ補正(％)')
    ctype_customer_correction = JsonCharField(default=dict, verbose_name=u'キャスト属性集客補正(％)')
    ctype_proceeds_correction = JsonCharField(default=dict, verbose_name=u'キャスト属性売上補正(％)')
    
    for attr in ('cr_correction',):
        for rare in Defines.Rarity.LIST:
            exec """def get_{attr}_{name}(self):
    return self.{attr}.get('{rare}', 100)""".format(attr=attr, rare=rare, name=Defines.Rarity.NAMES[rare].lower())
            exec """def set_{attr}_{name}(self, v):
    self.{attr}['{rare}']=v""".format(attr=attr, rare=rare, name=Defines.Rarity.NAMES[rare].lower())
    
    for attr in ('ctype_customer_correction', 'ctype_proceeds_correction'):
        for ctype in Defines.CharacterType.LIST:
            exec """def get_{attr}_{ctype}(self):
    return self.{attr}.get('{ctype}', 100)""".format(attr=attr, ctype=ctype)
            exec """def set_{attr}_{ctype}(self, v):
    self.{attr}['{ctype}']=v""".format(attr=attr, ctype=ctype)

class CabaClubEventMaster(BaseMasterWithThumbnail):
    """キャバクラ店舗で発生するイベントのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    seconds = models.PositiveIntegerField(default=0, verbose_name=u'発生時間(秒)')
    customer_up = models.PositiveSmallIntegerField(default=100, verbose_name=u'集客数補正(％)')
    proceeds_up = models.PositiveSmallIntegerField(default=100, verbose_name=u'売上補正(％)')
    ua_type = models.PositiveSmallIntegerField(default=Defines.CabaClubEventUAType.NONE, verbose_name=u'ユーザーアクションの種類', choices=Defines.CabaClubEventUAType.NAMES.items())
    ua_value = models.PositiveSmallIntegerField(default=0, verbose_name=u'ユーザーアクションの効果の値')
    ua_cost = models.PositiveIntegerField(default=0, verbose_name=u'ユーザーアクションの消費される特殊マネーの消費量')
    ua_text = models.TextField(default='', verbose_name=u'ユーザーアクションの効果の文言', blank=True)

class CabaClubStoreMaster(BaseMasterWithThumbnail):
    """キャバクラ店舗のマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    days_0 = models.PositiveSmallIntegerField(default=0, verbose_name=u'レンタル期間(日)_0')
    cost_0 = models.PositiveIntegerField(default=0, verbose_name=u'レンタル費_0')
    days_1 = models.PositiveSmallIntegerField(default=0, verbose_name=u'レンタル期間(日)_1')
    cost_1 = models.PositiveIntegerField(default=0, verbose_name=u'レンタル費_1')
    days_2 = models.PositiveSmallIntegerField(default=0, verbose_name=u'レンタル期間(日)_2')
    cost_2 = models.PositiveIntegerField(default=0, verbose_name=u'レンタル費_2')
    days_3 = models.PositiveSmallIntegerField(default=0, verbose_name=u'レンタル期間(日)_3')
    cost_3 = models.PositiveIntegerField(default=0, verbose_name=u'レンタル費_3')
    days_4 = models.PositiveSmallIntegerField(default=0, verbose_name=u'レンタル期間(日)_4')
    cost_4 = models.PositiveIntegerField(default=0, verbose_name=u'レンタル費_4')
    customer_interval = models.PositiveIntegerField(default=0, verbose_name=u'客が入る間隔(秒)')
    proceeds_rand_min = models.PositiveSmallIntegerField(default=100, verbose_name=u'売上の乱数下限(％)')
    proceeds_rand_max = models.PositiveSmallIntegerField(default=100, verbose_name=u'売上の乱数上限(％)')
    customer_rand_min = models.PositiveSmallIntegerField(default=100, verbose_name=u'集客数の乱数下限')
    customer_rand_max = models.PositiveSmallIntegerField(default=100, verbose_name=u'集客数の乱数上限')
    customer_max = models.PositiveIntegerField(default=0, verbose_name=u'集客数の最大値(最大収容人数)')
    cast_num_max = models.PositiveSmallIntegerField(default=0, verbose_name=u'キャストの人数の上限')
    scoutman_num_max = models.PositiveSmallIntegerField(default=0, verbose_name=u'スカウトマン数の基本値')
    scoutman_add_max = models.PositiveSmallIntegerField(default=0, verbose_name=u'スカウトマン数の増加の上限')
    events = JsonCharField(default=list, verbose_name=u'発生するイベントテーブル', help_text=u'[[イベントID,発生率(1-10000)],...]')

class CabaClubStorePlayerData(BasePerPlayerBaseWithMasterID):
    """キャバクラ店舗のプレイヤーデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    rtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'借りた時間')
    ltime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'借用期限')
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後にイベントを確認した日時')
    utime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後に集客を更新した日時')
    event_id = models.PositiveIntegerField(default=0, verbose_name=u'発生中のイベント')
    scoutman_add = models.PositiveSmallIntegerField(default=0, verbose_name=u'増加したスカウトマン数')
    is_open = models.BooleanField(default=False, verbose_name=u'開店フラグ')
    octime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'最後に状態を更新した日時')
    ua_flag = models.BooleanField(default=False, verbose_name=u'ユーザーアクション実行フラグ')
    proceeds = PositiveBigIntegerField(default=0, verbose_name=u'総売上')
    customer = PositiveBigIntegerField(default=0, verbose_name=u'総集客数')

class CabaClubCastPlayerData(BasePerPlayerBaseWithMasterID):
    """キャバクラ店舗のキャスト配属情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    cast = ObjectField(default=list, verbose_name=u'配属されているキャスト')

class CabaClubItemPlayerData(BaseModel):
    """キャバクラ店舗のアイテム情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    preferential_id = models.PositiveIntegerField(default=0, verbose_name=u'優待券のID')
    preferential_time = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'優待券の有効期限')
    barrier_id = models.PositiveIntegerField(default=0, verbose_name=u'バリアアイテムのID')
    barrier_time = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'バリアアイテムの有効期限')

class CabaClubScorePlayerData(BaseModel):
    """キャバクラ店舗の総スコア情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    money = models.PositiveIntegerField(default=0, verbose_name=u'特別なマネー')
    point = models.PositiveIntegerField(default=0, verbose_name=u'名誉ポイント')

class CabaClubScorePlayerDataWeekly(BaseModel):
    """キャバクラ店舗の週間スコア情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(default=0, verbose_name=u'ユーザID')
    week = models.PositiveIntegerField(default=0, verbose_name=u'年と週')
    proceeds = PositiveBigIntegerField(default=0, verbose_name=u'売上')
    customer = PositiveBigIntegerField(default=0, verbose_name=u'集客数')
    flag_aggregate = models.BooleanField(default=False, verbose_name=u'集計フラグ')
    view_result = models.BooleanField(default=False, verbose_name=u'結果閲覧フラグ')
    
    @staticmethod
    def makeID(uid, etime):
        week = int(etime.strftime("%Y%W"))
        return (uid << 32) + week
    
    @classmethod
    def makeInstance(cls, key):
        ins = cls()
        ins.id = key
        ins.uid = int(key >> 32)
        ins.week = int(key & 0xffffffff)
        return ins

