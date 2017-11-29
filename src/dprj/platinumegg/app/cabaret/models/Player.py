# -*- coding: utf-8 -*-
import settings
import settings_sub
from django.db import models
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.base.models import BaseModel
from platinumegg.app.cabaret.models.base.fields import PositiveBigIntegerField,\
    PositiveAutoField, AppDateTimeField, ObjectField
from defines import Defines
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.models.base.util import dict_to_choices


class Player(BaseModel):
    """プレイヤー基礎情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    
    FIXED_COLUMNS = (
        'dmmid','itime',
    )
    
    id = PositiveAutoField(primary_key=True, verbose_name=u'ユーザID')
    dmmid = models.CharField(max_length=16, unique=True, verbose_name=u'ユーザID(DMM)')
    itime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'インストール時間')
    preregist = models.BooleanField(default=False, verbose_name=u'事前登録')

class RelatedName:
    def __init(self, model_cls):
        self.__model_cls = model_cls
    def __str__(self):
        return self.__model_cls.__name__.lower()

class BasePerPlayerBase(BaseModel):
    """ユーザー*アイテムでユニークな情報.
    """
    class Meta:
        abstract = True
    
    FIXED_COLUMNS = (
        'uid','mid',
    )
    
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ID((ユーザID<<32)+アイテムID')
    uid = models.PositiveIntegerField(db_index=True, verbose_name=u'ユーザID')
    mid = None  # それぞれのテーブルで実装しないとダメ.
    
    @classmethod
    def makeID(cls, uid, mid):
        return (uid << 32) + mid
    
    @classmethod
    def makeInstance(cls, key):
        model = cls()
        primary_key_column = cls.get_primarykey_column()
        setattr(model, primary_key_column, key)
        model.uid = (key >> 32)
        model.mid = key & 0xffffffff
        return model
    
    def get_write_end_methods(self):
        """書き込み（更新、削除）がされたら呼ばれるメソッド.
        """
        pass
    
    @classmethod
    def fetchByOwner(cls, uid, using=settings.DB_READONLY):
        filters = {
            'uid' : uid,
        }
        ret = cls.fetchValues(filters=filters, using=using)
        return ret

class BasePerPlayerBaseWithMasterID(BasePerPlayerBase):
    """ユーザー*アイテムでユニークな情報.
    """
    class Meta:
        abstract = True
    
    mid = models.PositiveIntegerField(db_index=True, verbose_name=u'アイテムID')

#===============================================================================
# Playerの細かい情報はここから.
class PlayerLimitation(BaseModel):
    """プレイヤーにかける制限.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    ban = models.BooleanField(default=False, db_index=True, verbose_name=u'停止フラグ')

class PlayerRegist(BaseModel):
    """登録時に設定する内容.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    ctime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'登録時間')
    ptype = models.PositiveSmallIntegerField(db_index=True, choices=dict_to_choices(Defines.CharacterType.NAMES), verbose_name=u'タイプ')

class PlayerTutorial(BaseModel):
    """チュートリアル情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    tutorialstate = models.PositiveIntegerField(verbose_name=u'チュートリアルの進行状態')
    etime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'チュートリアル完了時間')
    
    @property
    def returns_tutorialstate(self):
        """復帰用チュートリアル状態.
        """
        return self.tutorialstate & 0xff00

class PlayerExp(BaseModel):
    """プレイヤー経験値.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    exp = models.PositiveIntegerField(default=0, verbose_name=u'経験値')
    level = models.PositiveIntegerField(default=1, db_index=True, verbose_name=u'レベル')
    hp = models.PositiveIntegerField(default=0, verbose_name=u'ボス戦用のHP')

class PlayerGold(BaseModel):
    """プレイヤーの所持ポケットマネー.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    gold = models.PositiveIntegerField(default=0, verbose_name=u'ポケットマネー')

class PlayerAp(BaseModel):
    """プレイヤーの行動力.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    ap = models.PositiveSmallIntegerField(default=0, verbose_name=u'体力')
    apmax = models.PositiveSmallIntegerField(default=10, verbose_name=u'体力最大値')
    aprtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'体力を書き込んだ時間')
    bp = models.PositiveSmallIntegerField(default=0, verbose_name=u'気力')
    bprtime = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'気力を書き込んだ時間')
    bpmax = 100 # 100固定に.
    
    AP_COLUMN_NAME = 'ap'
    BP_COLUMN_NAME = 'bp'
    AP_TIME_COLUMN_BASE = '%srtime'
    AP_MAX_COLUMN_BASE = '%smax'
    AP_RECOVE_TIME_TABLE = {
        AP_COLUMN_NAME:Defines.AP_RECOVE_TIME,
        BP_COLUMN_NAME:Defines.BP_RECOVE_TIME,
    }
    

class PlayerDeck(BaseModel):
    """デッキ関係.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    deckcapacitylv = models.PositiveSmallIntegerField(default=10,verbose_name=u'デッキコスト上限(Lvup)')
    deckcapacityscout = models.PositiveSmallIntegerField(default=0,verbose_name=u'デッキコスト上限(スカウト)')
    cardlimitlv = models.PositiveSmallIntegerField(default=0,verbose_name=u'カード所持数上限(Lvup)')
    cardlimititem = models.PositiveSmallIntegerField(default=0,verbose_name=u'カード所持数上限(アイテム)')
    deckcost = models.PositiveSmallIntegerField(default=0, verbose_name=u'デッキコスト値')

    @property
    def cardlimit(self):
        self.cardlimitlv=300
        return self.cardlimitlv + self.cardlimititem
    @property
    def deckcapacity(self):
        return self.deckcapacitylv + self.deckcapacityscout

class PlayerFriend(BaseModel):
    """フレンド関係.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    friendnum = models.PositiveSmallIntegerField(default=0, verbose_name=u'現在仲間人数')
    friendlimit = models.PositiveSmallIntegerField(default=0, verbose_name=u'仲間上限')

class PlayerGachaPt(BaseModel):
    """引きぬきポイント関係.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    gachapt = models.PositiveIntegerField(default=0, verbose_name=u'引き抜きPt')
    rareoverticket = models.PositiveIntegerField(default=0, verbose_name=u'レア以上チケット')
    memoriesticket = models.PositiveIntegerField(default=0, verbose_name=u'思い出チケット')
    tryluckticket = models.PositiveIntegerField(default=0, verbose_name=u'運試しチケット')
    gachaticket = models.PositiveIntegerField(default=0, verbose_name=u'引き抜きチケット')

class PlayerTreasure(BaseModel):
    """秘宝関係.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    cabaretking = models.PositiveIntegerField(default=0, verbose_name=u'キャバ王の秘宝')
    demiworld = models.PositiveIntegerField(default=0, verbose_name=u'裏社会の秘宝')
    
    def get_cabaretking_num(self):
        """秘宝一本化.
        """
        return self.cabaretking + self.demiworld

class PlayerPlatinumPiece(BaseModel):
    """プラチナの欠片.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    count = models.PositiveIntegerField(default=0, verbose_name=u'プラチナの欠片の個数')

class PlayerCrystalPiece(BaseModel):
    """クリスタルの欠片
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザーID')
    count = models.PositiveIntegerField(default=0, verbose_name=u'クリスタルの欠片の個数')

class PlayerTradeShop(BaseModel):
    """Pt 交換所に関するユーザに紐づくポイント.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = PositiveBigIntegerField(primary_key=True, verbose_name=u'ユーザID)')
    point = models.PositiveIntegerField(default=0, verbose_name=u'point')

    @classmethod
    def get(cls, model_mgr, id):
        model_mgr.get_model(cls,id,using=settings.DB_READONLY)

    @classmethod
    def createInstance(cls, uid):
        ins = cls()
        ins.point = 0
        ins.id = uid
        
        return ins

class PlayerKey(BaseModel):
    """鍵.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    goldkey = models.PositiveIntegerField(default=0, verbose_name=u'金の鍵')
    silverkey = models.PositiveIntegerField(default=0, verbose_name=u'銀の鍵')

class PlayerScout(BaseModel):
    """スカウト関係.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    lastscout = models.PositiveIntegerField(default=0, verbose_name=u'最後にプレイしたスカウト')

class PlayerCard(BaseModel):
    """カード関係.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    card = models.PositiveIntegerField(default=0, verbose_name=u'カード番号')

class PlayerLogin(BaseModel):
    """ログイン情報.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    ltime = AppDateTimeField(default=OSAUtil.get_now, db_index=True, verbose_name=u'最終ログイン時間')
    ldays = models.PositiveSmallIntegerField(default=0, verbose_name=u'連続ログイン日数')
    pdays = models.PositiveSmallIntegerField(default=0, verbose_name=u'プレイ日数')
    lbtime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'ログインボーナス受取り時間')
    tldays_view = models.PositiveSmallIntegerField(default=0, verbose_name=u'累計ログイン日数')
    tldays = models.PositiveSmallIntegerField(default=0, verbose_name=u'累計ログイン日数(報酬用)')
    tlmid = models.PositiveIntegerField(default=0, verbose_name=u'最後に受け取った累計ログインボーナスのマスターID')
    
    def getDays(self, tlmid):
        if 0 < tlmid and self.tlmid == tlmid:
            return self.tldays
        else:
            return 0
    
    def getDaysView(self, tlmid):
        if 0 < tlmid and self.tlmid == tlmid:
            return self.tldays_view
        else:
            return 0

class PlayerLoginTimeLimited(BaseModel):
    """期限付きログイン情報(廃止予定).
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    days = models.PositiveSmallIntegerField(default=0, verbose_name=u'プレイ日数')
    mid = models.PositiveIntegerField(default=0, verbose_name=u'最後に受け取ったログインボーナスのマスターID')
    lbtltime = AppDateTimeField(default=OSAUtil.get_datetime_min, verbose_name=u'区間別ログインボーナス受取り時間')
    
    def getDays(self, mid):
        if 0 < mid and self.mid == mid:
            return self.days
        else:
            return 0

class PlayerComment(BaseModel):
    """プロフィールコメント.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    commentid = models.CharField(max_length=32, verbose_name=u'プロフィールコメントID')

class PlayerHappening(BaseModel):
    """ハプニング.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    happening = models.PositiveIntegerField(default=0, verbose_name=u'ハプニング番号')
    happening_seed = models.PositiveIntegerField(default=AppRandom.makeSeed, verbose_name=u'乱数シード')
    happening_result = ObjectField(default=dict, verbose_name=u'前回の実行結果')

class PlayerRequest(BaseModel):
    """リクエストのキー.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    req_confirmkey = models.CharField(max_length=20, default=OSAUtil.makeSessionID, verbose_name=u'重複確認用のキー')
    req_alreadykey = models.CharField(max_length=20, default='', verbose_name=u'重複確認用のキー')

class PlayerConsumePoint(BaseModel):
    """生涯課金額.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    point_total = models.PositiveIntegerField(default=0, verbose_name=u'生涯課金額')

class RareCardLog(BaseModel):
    """レアキャバ嬢獲得履歴.
    """
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    card0 = models.PositiveIntegerField(default=0, verbose_name=u'獲得したカード 最新')
    gtime0 = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'獲得した時間 最新')
    card1 = models.PositiveIntegerField(default=0, verbose_name=u'獲得したカード 1個前')
    gtime1 = AppDateTimeField(default=OSAUtil.get_now, verbose_name=u'獲得した時間 1個前')
    
    def add(self, cardmasterid):
        self.card1 = self.card0
        self.gtime1 = self.gtime0
        self.card0 = cardmasterid
        self.gtime0 = OSAUtil.get_now()
    
    def to_array(self):
        arr = []
        for cid, gtime in [(self.card0, self.gtime0), (self.card1, self.gtime1)]:
            if cid:
                arr.append({'card':cid, 'time':gtime})
        return arr

class PlayerCrossPromotion(BaseModel):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    total_login_count = models.PositiveIntegerField(default=0, verbose_name=u'期間中の累計ログインボーナス日数')
    is_open_cabaclub = models.BooleanField(default=False, verbose_name=u'期間中に経営をしたか')
    is_battle = models.BooleanField(default=False, verbose_name=u'期間中にキャバ道をしたか')
    is_battle_win_continue = models.BooleanField(default=False, verbose_name=u'期間中にキャバ道で連勝をしたか')
    is_battle_rank5 = models.BooleanField(default=False, verbose_name=u'期間までにキャバ道のレベルが5になったか')
    is_level10 = models.BooleanField(default=False, verbose_name=u'期間迄にレベル10になったか')
    is_level20 = models.BooleanField(default=False, verbose_name=u'期間迄にレベル20になったか')
    is_trade_treasure = models.BooleanField(default=False, verbose_name=u'期間中に秘宝を交換したか')
    is_acquired_ssr_card = models.BooleanField(default=False, verbose_name=u'SSRキャストをゲットしたか')

    @classmethod
    def makeInstance(cls, key):
        new_model = cls()
        new_model.id = key
        new_model.total_login_count = 0
        new_model.is_open_cabaclub = False
        new_model.is_battle = False
        new_model.is_battle_win_continue = False
        new_model.is_battle_rank5 = False
        new_model.is_level10 = False
        new_model.is_level20 = False
        new_model.is_trade_treasure = False
        return new_model

    @classmethod
    def is_session(cls):
        return Defines.CROSS_PROMO_START_TIME < OSAUtil.get_now() < Defines.CROSS_PROMO_END_TIME

    @classmethod
    def update_player_cross_promotion(cls, model_mgr, uid, *target_fields):
        if not set(target_fields) <= set(cls._meta.get_all_field_names()):
            raise CabaretError(u'target_fieldsの指定が不正です')

        player_crosspromo = model_mgr.get_model(cls, uid, using=settings.DB_READONLY)

        def forUpdateCrossPromotion(model, inserted):
            for field in target_fields:
                if field == "total_login_count":
                    model.total_login_count += 1
                elif getattr(model, field) is False:
                    setattr(model, field, True)

        def need_update(x):
            return getattr(player_crosspromo, x) is False or type(getattr(player_crosspromo, x)) in {int, long}

        if player_crosspromo is None or any(map(need_update, target_fields)):
            model_mgr.add_forupdate_task(cls, uid, forUpdateCrossPromotion)


class PlayerDXPWallConversion(BaseModel):
    class Meta:
        app_label = settings_sub.APP_NAME
        abstract = False
    id = models.PositiveIntegerField(primary_key=True, verbose_name=u'ユーザID')
    is_set_conversion = models.BooleanField(default=False, verbose_name=u'コンバージョンの設定をしたか')
    is_set_incentive = models.BooleanField(default=False, verbose_name=u'インセンティブの設定をしたか')
    is_prize_incentive = models.BooleanField(default=False, verbose_name=u'インセンティブを配布したか')
    is_received = models.BooleanField(default=False, verbose_name=u'ユーザがインセンティブを受け取ったか')

