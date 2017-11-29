# *-*- coding: utf-8 -*-

import settings, settings_sub
from django.db import models
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.models import BaseMaster, Singleton
from platinumegg.app.cabaret.models.base.fields import JsonCharField, AppDateTimeField, PositiveBigIntegerField, \
    PositiveBigAutoField, TinyIntField, ObjectField
from platinumegg.app.cabaret.models.Player import BasePerPlayerBase
from platinumegg.app.cabaret.models.EventScout import EventScoutStageMaster, EventScoutPlayData
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Card import CardMaster
from defines import Defines
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.app.cabaret.models.base.util import get_pointprizes

class ProduceEventMaster(BaseMaster):
    """プロデュースイベントのマスターデータです
    """

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    name = models.CharField(verbose_name=u'名前', max_length=48)
    subname = models.CharField(verbose_name=u'イベントサブタイトル', max_length=64, blank=True, default='')
    htmlname = models.CharField(verbose_name=u'HTML演出ディレクトリ名', max_length=48)
    rankingprizes = JsonCharField(verbose_name=u'ランキング報酬')
    rankingprize_text = models.PositiveIntegerField(verbose_name=u'ランキング報酬文言')
    pointprizes = JsonCharField(verbose_name=u'ポイント達成報酬')
    pointprize_text = models.PositiveIntegerField(verbose_name=u'ポイント達成報酬文言')
    raidtable = JsonCharField(verbose_name=u'レイド出現テーブル')
    raidtable_big = JsonCharField(verbose_name=u'大ボス出現後レイド出現テーブル')
    raidtable_full = JsonCharField(verbose_name=u'レイド出現テーブル(全力探索)')
    raidtable_big_full = JsonCharField(verbose_name=u'大ボス出現後レイド出現テーブル(全力探索)')
    useitem = models.PositiveSmallIntegerField(verbose_name=u'超接客で使用するアイテムID')
    changeitem = models.PositiveSmallIntegerField(verbose_name=u'専用アイテムと交換するためのアイテムID')
    op = models.PositiveIntegerField(default=0, verbose_name=u'オープニング演出ID')
    ed = models.PositiveIntegerField(default=0, verbose_name=u'エンディング演出ID')
    specialcard = JsonCharField(default=list, verbose_name=u'特効カード', help_text=u'[[カードID,倍率],[カードID,倍率],...]')
    img_appeal = JsonCharField(default=list, verbose_name=u'訴求画像リスト', blank=True)

    @property
    def codename(self):
        return self.htmlname.split('/')[-1]

    def get_produce_castmasters(self, filters=None, order_by=None, using=settings.DB_DEFAULT):
        filter_dict = {'event_id': self.id}
        if isinstance(filters, dict):
            filter_dict.update(filters)
        masters = ProduceCastMaster.fetchValues(filters=filter_dict, order_by=order_by, using=using)
        if not masters:
            raise CabaretError(u'プロデュースキャストが設定されていません', code=CabaretError.Code.INVALID_MASTERDATA)
        return masters

    def get_pointprizes(self, point_min=1, point_max=None):
        return get_pointprizes(self.pointprizes, point_min, point_max)

class CurrentProduceEventConfig(Singleton):
    """開催中または開催予定のプロデュースイベント.
    """

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    mid = models.PositiveIntegerField(default=0, verbose_name=u'イベントのマスターID')
    starttime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'開始時間')
    endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'終了時間')
    bigtime = AppDateTimeField(default=OSAUtil.get_datetime_max, verbose_name=u'大ボス出現時間')
    epilogue_endtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'エピローグ終了時間')

    def is_open_event(self, target_time):
        return self.starttime <= target_time < self.endtime

    def is_open_epilogue(self, target_time):
        return self.endtime <= target_time < self.epilogue_endtime

    def get_produce_event_master(self, model_mgr, using=settings.DB_DEFAULT):
        produce_event_master = model_mgr.get_model(ProduceEventMaster, self.mid, using=using)
        if not produce_event_master:
            raise CabaretError(u'対応するProduceEventMasterが存在しません', code=CabaretError.Code.INVALID_MASTERDATA)
        return produce_event_master

class ProduceCastMaster(BaseMaster):
    """プロッデュースキャストのマスターデータ
    """

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ID')
    event_id = models.PositiveIntegerField(default=0, verbose_name=u'イベントID')
    order = models.PositiveIntegerField(default=0, verbose_name=u'教育の順番')
    produce_cast = models.PositiveIntegerField(default=0, verbose_name=u'イベント使用キャスト')
    lvprizes = JsonCharField(verbose_name=u'教育Lv達成報酬')
    lvprize_text = models.PositiveIntegerField(verbose_name=u'教育Lv達成報酬文言')
    produce_cast_talk_good = models.CharField(default='', max_length=500, verbose_name=u'接客成功セリフ')
    produce_cast_talk_perfect = models.CharField(default='', max_length=500, verbose_name=u'接客大成功時セリフ')
    education_point_good = models.PositiveIntegerField(default=0, verbose_name=u'成功時獲得教育ポイント')
    education_point_perfect = models.PositiveIntegerField(default=0, verbose_name=u'大成功時獲得教育ポイント')
    max_education_level = models.PositiveIntegerField(default=0, verbose_name=u'教育Lv最大値')
    complete_prizetext = models.PositiveIntegerField(verbose_name=u'コンプリート時にプレゼントする際の文言')
    
    @staticmethod
    def get_maxorder(produce_cast_masters):
        return max([cast.order for cast in produce_cast_masters])

    @staticmethod
    def get_max_maxeducationlevel(produce_cast_masters):
        return max([cast.max_education_level for cast in produce_cast_masters])

    def get_card(self, model_mgr, using=settings.DB_DEFAULT):
        card_master = model_mgr.get_model(CardMaster, self.produce_cast, using=using)
        if not card_master:
            raise CabaretError(u'対応するCardMasterが存在しません', code=CabaretError.Code.INVALID_MASTERDATA)
        return card_master

    @staticmethod
    def select_produce_cast_master(produce_cast_masters, order):
        produce_castmasters = [master for master in produce_cast_masters if master.order == order]
        if not produce_castmasters:
            raise CabaretError(u'Orderに対応するProduceCastMasterが存在しません', code=CabaretError.Code.INVALID_MASTERDATA)
        return produce_castmasters[0]

    def get_point(self, is_perfect_win):
        if is_perfect_win:
            return self.education_point_perfect
        else:
            return self.education_point_good

    def get_prizeidlist(self, level):
        for prize in self.lvprizes:
            if prize['level'] == level:
                return prize['prize']

    def to_dict(self):
        return {"produce_cast_talk_good":self.produce_cast_talk_good, "produce_cast_talk_perfect":self.produce_cast_talk_perfect}

class ProduceEventScoutStageMaster(EventScoutStageMaster):
    """イベントスカウトのステージマスターデータ.
    """

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    apcost_full = models.PositiveSmallIntegerField(verbose_name=u'全力探索時の消費体力')
    eventrate_happening_full = models.PositiveSmallIntegerField(verbose_name=u'全力探索のハプニング発生率')
    eventrate_treasure_full = models.PositiveSmallIntegerField(verbose_name=u'全力探索の宝箱発見発生率')

class ProduceEventScoutPlayData(EventScoutPlayData):
    """プロデュースイベントの進行情報
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    def setResult(self, result, eventlist, flag_earlybonus=False):
        self._setResult(result, eventlist, flag_earlybonus)


class ProduceEventRaidMaster(BaseMaster):
    """プロデュースレイドのマスターデータ
    """

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    id = PositiveBigIntegerField(verbose_name=u'ID', primary_key=True)
    eventid = models.PositiveIntegerField(verbose_name=u'プロデュースイベントマスターID', db_index=True)
    mid = models.PositiveIntegerField(verbose_name=u'レイドマスターID', db_index=True)
    ptbase = models.PositiveIntegerField(verbose_name=u'基礎獲得値')
    good_coefficient = models.PositiveIntegerField(verbose_name=u'成功係数')
    perfect_coefficient = models.PositiveIntegerField(verbose_name=u'大成功係数')
    perfect_probability = models.PositiveIntegerField(verbose_name=u'大成功確率')
    big = models.BooleanField(default=False, verbose_name=u'大ボスフラグ')

class ProduceEventFlags(BasePerPlayerBase):
    """プロデュースイベントフラグ.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    opvtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'OP演出閲覧時間')
    epvtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'EP演出閲覧時間')

    @staticmethod
    def get_instance(model_mgr, uid, eventmaster_id, using=settings.DB_DEFAULT):
        model = model_mgr.get_model(ProduceEventFlags, ProduceEventFlags.makeID(uid, eventmaster_id), get_instance=True, using=using)
        return model

class ProduceEventScore(BasePerPlayerBase):
    """プロデュースイベントのランキング用スコア
    """

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    point = models.PositiveIntegerField(verbose_name=u'所持ポイント', default=0)
    destroy = models.PositiveIntegerField(default=0, verbose_name=u'討伐回数')
    destroy_big = models.PositiveIntegerField(default=0, verbose_name=u'討伐回数(大ボス)')
    
    def to_dict(self):
        return {"mid":self.mid, "point":self.point, "destroy":self.destroy, \
        "destroy_big":self.destroy_big}

    @staticmethod
    def get_instance(model_mgr, uid, eventmaster_id, using=settings.DB_DEFAULT):
        model = model_mgr.get_model(ProduceEventScore, ProduceEventScore.makeID(uid, eventmaster_id), using=using)
        if not model:
            model = ProduceEventScore.make_instance(uid, eventmaster_id)
        return model

    @staticmethod
    def make_instance(uid, eventmaster_id):
        model = ProduceEventScore.makeInstance(ProduceEventScore.makeID(uid, eventmaster_id))
        return model

class ProduceEventHappening(BaseModel):
    """プロでハプニング本体.
    """

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    FIXED_COLUMNS = (
        'oid', 'mid', 'ctime', 'level', 'hprate', 'event',
        'gold', 'items'  # ここはハプニングが無いから固定.
    )

    id = PositiveBigAutoField(primary_key=True, verbose_name=u'ID')
    oid = models.PositiveIntegerField(db_index=True, verbose_name=u'発見者')
    mid = models.PositiveIntegerField(verbose_name=u'マスターID')
    state = TinyIntField(default=Defines.HappeningState.ACTIVE, verbose_name=u'状態')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'発生時間')
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
        return self.state == Defines.HappeningState.END

    def is_cleared(self):
        return self.state == Defines.HappeningState.CLEAR

    def is_boss_appeared(self):
        return self.state == Defines.HappeningState.BOSS

    def is_active(self):
        return not (self.is_cleared() or self.is_end())

    def is_canceled(self):
        return False

    @staticmethod
    def makeDropItemName(itype, mid):
        return (itype << 32) + mid

    def addDropItem(self, itype, mid):
        """ドロップアイテムを追加.
        """
        if not itype in (Defines.ItemType.ITEM, Defines.ItemType.CARD):
            raise CabaretError(u'ハプニング未対応のドロップです.タイプ=%s' % Defines.ItemType.NAMES.get(itype, itype))
        key = ProduceEventHappening.makeDropItemName(itype, mid)
        num = self.items.get(key, 0)
        self.items[key] = num + 1

    def idDropped(self, itype, mid):
        """ドロップしたか.
        """
        return self.items and ProduceEventHappening.makeDropItemName(itype, mid) in self.items

class ProduceEventHappeningResult(BasePerPlayerBase):
    """プロデュースイベントのハプニング結果を保存する場所.
    Result画面の結果や、演出を表示する為に使う.
    1ユーザにつきイベント毎に1レコードのみ
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'プロデュースイベントマスターのID')
    event_point = models.PositiveIntegerField(default=0, verbose_name=u'イベントポイント')
    education_point = models.PositiveIntegerField(default=0, verbose_name=u'教育ポイント')
    before_heart = models.PositiveIntegerField(default=0, verbose_name=u'実行前のハート')
    before_level = models.PositiveIntegerField(default=0, verbose_name=u'実行前の教育レベル')
    after_level = models.PositiveIntegerField(default=0, verbose_name=u'実行後の教育レベル')
    order = models.PositiveIntegerField(default=0, verbose_name=u'レア度がいくつ上がったか')
    is_send_prize = models.BooleanField(default=False, verbose_name=u'プレゼントを送ったか')
    is_perfect_win = models.BooleanField(default=False, verbose_name=u'大成功したか')

    @staticmethod
    def get_instance(model_mgr, uid, eventmaster_id, using=settings.DB_DEFAULT):
        player_education = model_mgr.get_model(ProduceEventHappeningResult, ProduceEventHappeningResult.makeID(uid, eventmaster_id), using=using)
        if not player_education:
            player_education = ProduceEventHappeningResult.make_instance(uid, eventmaster_id)
        return player_education

    @staticmethod
    def make_instance(uid, eventmaster_id):
        player_education = ProduceEventHappeningResult.makeInstance(ProduceEventHappeningResult.makeID(uid, eventmaster_id))
        return player_education
    
    def to_dict(self):
        return {"event_point":self.event_point, "education_point":self.education_point, "before_heart":self.before_heart,  \
        "before_level":self.before_level, "after_level":self.after_level, "order":self.order, "is_send_prize":self.is_send_prize,
        "is_perfect_win":self.is_perfect_win}

class PlayerEducation(BasePerPlayerBase):
    """教育ポイントなど
    """
    MAX_HEART = 5

    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False

    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'イベントのマスターID')
    level = models.PositiveIntegerField(verbose_name=u'教育レベル')
    heart = models.PositiveIntegerField(default=0, verbose_name=u'ハート')
    cast_order = models.PositiveIntegerField(default=1, verbose_name=u'今が何番目のキャストか')

    @staticmethod
    def make_instance(uid, eventmaster_id):
        player_education = PlayerEducation.makeInstance(PlayerEducation.makeID(uid, eventmaster_id))
        player_education.level = 1
        player_education.mid = eventmaster_id
        return player_education
        
    def get_produce_castmaster_for_array(self, produce_cast_masters):
        return ProduceCastMaster.select_produce_cast_master(produce_cast_masters, self.cast_order)

    def get_produce_castmaster(self):
        masters = ProduceCastMaster.fetchValues(filters={'event_id': self.mid, 'order': self.cast_order})
        
        if not masters:
            raise CabaretError(u'cast_orderに対応するプロデュースキャストが設定されていません', code=CabaretError.Code.INVALID_MASTERDATA)
        return masters[0]

    def is_education_limit(self, max_level, max_order):
        return self.level == max_level and self.heart == self.MAX_HEART and self.cast_order == max_order
        
    def add_point(self, num, max_level, max_order):
        heartup_num = num
        levelup_num = ((self.heart + heartup_num) - 1) / self.MAX_HEART
        orderup_num = (levelup_num + self.level) / (max_level+1)

        if self.cast_order >= max_order:
            orderup_num = 0
            if self.level >= max_level:
                levelup_num = 0
                if self.heart >= self.MAX_HEART:
                    heartup_num = 0
        
        new_heart = (self.heart + heartup_num) % (self.MAX_HEART+1)
        new_level = (levelup_num + self.level) % (max_level+1)
        new_order = min(self.cast_order + orderup_num, max_order)
        
        if self.cast_order >= max_order:
            if (levelup_num + self.level) >= max_level:
                if (self.heart + heartup_num) >= self.MAX_HEART:#キャストがMaxで、MAXLEVELの場合は、ハートはリセットしない
                    new_heart = self.MAX_HEART

        if orderup_num > 0:##レア度をまたぐ際にはポイントはリセットされる。
            new_level = 1
            new_heart = 0

        self.heart = new_heart
        self.level = new_level
        self.cast_order = new_order
        return heartup_num, levelup_num, orderup_num
