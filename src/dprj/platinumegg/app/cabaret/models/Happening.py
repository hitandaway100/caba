# -*- coding: utf-8 -*-
import settings_sub
from django.db import models
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.models import BaseMasterWithThumbnail,\
    BaseModel, BaseMaster
from platinumegg.app.cabaret.models.base.fields import ObjectField,\
    JsonCharField, TinyIntField, AppDateTimeField, PositiveBigIntegerField,\
    PositiveBigAutoField
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import BasePerPlayerBaseWithMasterID
from platinumegg.app.cabaret.models.Card import Card
from platinumegg.app.cabaret.models.base.util import dict_to_choices

class HappeningMaster(BaseMasterWithThumbnail):
    """ハプニングのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    execution = models.PositiveSmallIntegerField(verbose_name=u'クリアまでのポチポチ回数')
    apcost = models.PositiveSmallIntegerField(verbose_name=u'消費体力')
    exp = models.PositiveIntegerField(verbose_name=u'獲得経験値')
    goldmin = models.PositiveIntegerField(verbose_name=u'獲得ポケットマネー最小値')
    goldmax = models.PositiveIntegerField(verbose_name=u'獲得ポケットマネー最大値')
    items = JsonCharField(default=list, verbose_name=u'アイテム出現テーブル')
    timelimit = models.PositiveIntegerField(verbose_name=u'制限時間[sec]')
    boss = models.PositiveIntegerField(verbose_name=u'レイドボス')
    girls = JsonCharField(default=list, verbose_name=u'出現する女性')

class RaidMaster(BaseMaster):
    """レイドのマスターデータ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(default='', max_length=48, verbose_name=u'名前')
    commentappear = models.TextField(default='', verbose_name=u'出現時(挑発)コメント')
    commentwin = models.TextField(default='', verbose_name=u'勝利(ユーザが勝利)時コメント')
    commentwin_full = models.TextField(default='', verbose_name=u'大成功時コメント')
    commentlose = models.TextField(default='', verbose_name=u'敗北(ユーザが敗北)時コメント')
    thumb = models.CharField(default='', max_length=96, verbose_name=u'サムネイル')
    hprate_min = models.PositiveIntegerField(default=100, verbose_name=u'HPの変動幅の下限[%]')
    hprate_max = models.PositiveIntegerField(default=100, verbose_name=u'HPの変動幅の上限値[%]')
    hpbase = models.PositiveIntegerField(default=0, verbose_name=u'HP基本値')
    hpgrowth = models.PositiveIntegerField(default=0, verbose_name=u'HP成長度')
    defensebase = models.PositiveIntegerField(default=0, verbose_name=u'防御力基本値')
    defensegrowth = models.PositiveIntegerField(default=0, verbose_name=u'防御力成長度')
    bpcost = models.PositiveSmallIntegerField(default=20, verbose_name=u'気力消費量')
    bpcost_strong = models.PositiveSmallIntegerField(default=50, verbose_name=u'気力消費量(強攻撃)')
    bpcost_first = models.SmallIntegerField(default=-1, verbose_name=u'気力消費量(初回)', help_text=u'0より小さい場合は無効')
    bpcost_first_other = models.SmallIntegerField(default=-1, verbose_name=u'気力消費量(発見者以外の初回)', help_text=u'0より小さい場合は無効')
    prizes = JsonCharField(default=list, verbose_name=u'発見者の報酬')
    helpprizes = JsonCharField(default=list, verbose_name=u'救援の報酬')
    cabaretkingbase = models.PositiveIntegerField(default=0, verbose_name=u'キャバ王の秘宝基本値')
    cabaretkinggrowth = models.PositiveIntegerField(default=0, verbose_name=u'キャバ王の秘宝成長度')
    demiworldbase = models.PositiveIntegerField(default=0, verbose_name=u'キャバ王の秘宝(救援)基本値')
    demiworldgrowth = models.PositiveIntegerField(default=0, verbose_name=u'キャバ王の秘宝(救援)成長度')
    max_level = models.PositiveIntegerField(default=100, verbose_name=u'ボスの最大レベル')
    ctype = models.PositiveSmallIntegerField(verbose_name=u'ボスの属性', default=Defines.CharacterType.NONE, choices=dict_to_choices(Defines.CharacterType.BOSS_NAMES))
    weakbonus = JsonCharField(verbose_name=u'属性ボーナス', default=list, help_text=u'[[属性,倍率%],..]')
    items = JsonCharField(default=list, verbose_name=u'アイテム出現テーブル')

class Happening(BaseModel):
    """ハプニング本体.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    FIXED_COLUMNS = (
        'oid','mid','ctime','level','hprate','event',
        'gold','items'  # ここはハプニングが無いから固定.
    )
    
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    oid = models.PositiveIntegerField(db_index=True, verbose_name=u'発見者')
    mid = models.PositiveIntegerField(verbose_name=u'マスターID')
    state = TinyIntField(default=Defines.HappeningState.ACTIVE, verbose_name=u'状態')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'発生時間')
    etime = AppDateTimeField(db_index=True, default=OSAUtil.get_now, verbose_name=u'終了時間')
    progress = models.PositiveSmallIntegerField(default=0, verbose_name=u'進行度')
    gold = models.PositiveIntegerField(default=0, verbose_name=u'獲得ポケットマネー')
    items = ObjectField(default=dict, verbose_name=u'獲得アイテム')
    level = models.PositiveIntegerField(default=1, verbose_name=u'発生時のレベル')
    hprate = models.PositiveIntegerField(default=100, verbose_name=u'HPの変動率')
    event = PositiveBigIntegerField(default=0, verbose_name=u'イベントID')
    
    @staticmethod
    def makeID(uid, number):
        return (uid << 32) + number
    
    def is_end(self):
        return self.is_canceled() or self.is_missed() or self.state == Defines.HappeningState.END
    
    def is_canceled(self):
        return self.state == Defines.HappeningState.CANCEL
    
    def is_cleared(self):
        return self.state == Defines.HappeningState.CLEAR
    
    def is_missed(self):
        if self.state == Defines.HappeningState.MISS:
            return True
        return self.is_missed_and_not_end()
    
    def is_missed_and_not_end(self):
        if self.state in (Defines.HappeningState.ACTIVE, Defines.HappeningState.BOSS) and self.etime < OSAUtil.get_now():
            return True
        return False
    
    def is_boss_appeared(self):
        return self.state == Defines.HappeningState.BOSS
    
    def can_cancel(self):
        return self.state in (Defines.HappeningState.ACTIVE, Defines.HappeningState.BOSS)
    
    def is_active(self):
        return not (self.is_cleared() or self.is_end())
    
    @staticmethod
    def makeDropItemName(itype, mid):
        return (itype << 32) + mid
    
    def addDropItem(self, itype, mid):
        """ドロップアイテムを追加.
        """
        if not itype in (Defines.ItemType.ITEM, Defines.ItemType.CARD):
            raise CabaretError(u'ハプニング未対応のドロップです.タイプ=%s' % Defines.ItemType.NAMES.get(itype, itype))
        key = Happening.makeDropItemName(itype, mid)
        num = self.items.get(key, 0)
        self.items[key] = num + 1
    
    def idDropped(self, itype, mid):
        """ドロップしたか.
        """
        return self.items and Happening.makeDropItemName(itype, mid) in self.items

class Raid(BaseModel):
    """レイド本体.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    FIXED_COLUMNS = (
        'oid','mid','ctime','level','hprate',
        'timebonusflag','fastflag'
    )
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID')
    oid = models.PositiveIntegerField(db_index=True, verbose_name=u'発見者')
    mid = models.PositiveIntegerField(verbose_name=u'マスターID')
    level = models.PositiveIntegerField(default=1, verbose_name=u'レベル')
    hprate = models.PositiveIntegerField(default=100, verbose_name=u'HPの変動率')
    hp = models.PositiveIntegerField(default=1, verbose_name=u'残りHP')
    damage_record = ObjectField(default=dict, verbose_name=u'ダメージ履歴')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'発見した時間')
    helpflag = models.BooleanField(default=False, verbose_name=u'救援依頼を送ったか')
    timebonusflag = models.BooleanField(default=False, verbose_name=u'タイムボーナスフラグ')
    fastflag = models.BooleanField(default=False, verbose_name=u'秘宝ボーナスフラグ')
    
    def __formatDamageRecord(self):
        if not self.damage_record.has_key('damage'):
            self.damage_record = {
                'damage' : self.damage_record,
                'evpointrate' : 100,
            }
    
    def getDamageRecord(self):
        self.__formatDamageRecord()
        return self.damage_record['damage']
    
    def setDamageRecord(self, damage_record):
        self.__formatDamageRecord()
        self.damage_record['damage'] = damage_record
    
    @property
    def evpointrate(self):
        self.__formatDamageRecord()
        return self.damage_record['evpointrate']
    
    def setEvpointrate(self, evpointrate):
        self.__formatDamageRecord()
        self.damage_record['evpointrate'] = evpointrate

class RaidBattle(BaseModel):
    """レイドバトル情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    raidid = PositiveBigIntegerField(default=0, verbose_name=u'レイドID')
    process = ObjectField(default=dict, verbose_name=u'バトルの内容')
    helpcard = ObjectField(default=dict, verbose_name=u'助けてくれたフレンドのカード')
    is_strong = models.BooleanField(default=False, verbose_name=u'3倍攻撃フラグ')
    
    def setHelpCard(self, cardset):
        """助けてくれたフレンドを設定.
        """
        self.helpcard = {
            'id' : cardset.id,
            'oid' : cardset.card.uid,
            'mid' : cardset.master.id,
            'level' : cardset.card.level,
            'skilllevel' : cardset.card.skilllevel,
            'takeover' : cardset.card.takeover,
        }
    def getHelpCard(self):
        card = None
        if self.helpcard and isinstance(self.helpcard, dict):
            card = Card()
            card.id = self.helpcard['id']
            card.uid = self.helpcard['oid']
            card.mid = self.helpcard['mid']
            card.level = self.helpcard['level']
            card.skilllevel = self.helpcard['skilllevel']
            card.takeover = self.helpcard['takeover']
        return card

class RaidLog(BaseModel):
    """レイドログ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(verbose_name=u'ログの所有者')
    raidid = PositiveBigIntegerField(db_index=True, verbose_name=u'レイドID')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'発見した時間')

class RaidHelp(BaseModel):
    """救援依頼.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    fromid = models.PositiveIntegerField(db_index=True, verbose_name=u'ログの所有者')
    toid = models.PositiveIntegerField(verbose_name=u'ログの所有者')
    raidid = PositiveBigIntegerField(db_index=True, verbose_name=u'レイドID')
    raidevent_specialbonusscore = models.PositiveSmallIntegerField(default=0, verbose_name='レイドイベント時ボーナス特攻獲得UP倍率')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'発見した時間')
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間')

class RaidDestroyCount(BasePerPlayerBaseWithMasterID):
    """レイド討伐回数.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    cnt = models.PositiveIntegerField(default=0, verbose_name=u'討伐回数(リセットする想定)')
    total = models.PositiveIntegerField(default=0, verbose_name=u'総討伐回数')

class RaidPrizeDistributeQueue(BaseModel):
    """レイド成功報酬配布キュー.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    uid = models.PositiveIntegerField(default=0, verbose_name=u'このキューの作成者')
    raidid = PositiveBigIntegerField(verbose_name=u'レイドID')
