# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError, AppModelChoiceField
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventMaster, BattleEventPieceMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from platinumegg.app.cabaret.util.scout import ScoutHappeningSelector
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.app.cabaret.models.Card import CardMaster,CardSortMaster
import settings
import os, re

class Handler(AdminModelEditHandler):
    """.
    """
    class Form(AppModelForm):
        class Meta:
            model = BattleEventPieceMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        complete_prize_text = AppModelChoiceField(TextMaster, required=False, label=u'コンプリート報酬文言')
        complete_item_prize_text = AppModelChoiceField(TextMaster, required=False, label=u'コンプリート報酬代替アイテム配布文言')

    def setting_property(self):
        self.MODEL_LABEL = u'バトルピースイベント'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        self.__check_eventid(master.id,master.eventid)
        self.__check_item_lottery(master.id,master.item_lottery)
        self.__check_complete_prize(master.eventid,master.complete_prize)
        self.__check_number(master.id,master.number,master.complete_prize)
        self.__check_prizedir(master.id, master.name, master.complete_prize_name)

    def __check_eventid(self,master_id,event_id):
        if not self.__is_int(event_id):
            self.__raise_ModelEditValidError(master_id,(u'このイベントIDは整数ではありません'))

        if not self.__is_exist_event_masterid(event_id):
            self.__raise_ModelEditValidError(master_id,(u'%dというイベントIDはBattleEventMasterに存在しません' % event_id))

    def __check_number(self, master_id,number,card_id):
        """レアリティ用の通し番号"""
        # if not number+Defines.Rarity.HIGH_NORMAL+1 in range(Defines.Rarity.RARE,Defines.Rarity.SPECIALSUPERRARE+1):
        #     self.__raise_ModelEditValidError(master_id,(u'%dという値がレアリティ用の通し番号の値が範囲を超えています。' % number))
        
        # model_mgr = self.getModelMgr()
        # master = model_mgr.get_model(CardSortMaster, card_id, using=settings.DB_READONLY)
        # if master.rare != number + Defines.Rarity.HIGH_NORMAL + 1:
        #     self.__raise_ModelEditValidError(master_id,(u'%dというレア度通し番号と、コンプリート報酬のカードのレアリティが異なっています' % number))
        pass

    def __check_item_lottery(self,master_id,item_lottery):
        if not isinstance(item_lottery, list):
            self.__raise_ModelEditValidError(master_id,(u'アイテムドロップ率の抽選のJsonが壊れています'))
        for item_probability in item_lottery:
            if not isinstance(item_probability, dict):
                self.__raise_ModelEditValidError(master_id,(u'アイテムドロップ率の抽選のJsonが壊れています'))
            miss_key = self.__is_not_exist_probability_keys(item_probability)
            if miss_key:
                self.__raise_ModelEditValidError(master_id,(u'アイテムドロップ率のJson内に%sのキーが存在しません' % miss_key))
            if not self.__is_int(item_probability["rate"]):
                self.__raise_ModelEditValidError(master_id,(u'アイテムドロップ率の抽選の確率が整数ではありません。'))
            for prize_id in item_probability["prize"]:
                if not self.__is_exist_prizeid(prize_id):
                    self.__raise_ModelEditValidError(master_id,(u'prize_idの%dが存在しません' % prize_id))
        if not self.__is_total_100(item_lottery):
            self.__raise_ModelEditValidError(master_id,(u'アイテムドロップ率の抽選の確率の合計が100%ではありません'))

    def __check_complete_prize(self,master_id,card_id):
        if not self.__is_exist_cardid(card_id):
            self.__raise_ModelEditValidError(master_id,(u'コンプリート報酬で指定されているCardのid %d は存在しません' % card_id))

    def __raise_ModelEditValidError(self,master_id,message):
        raise ModelEditValidError(message + (' id=%d' % master_id))

    def __is_total_100(self,item_lottery):
        total = 0
        for item_probability in item_lottery:
            total += item_probability["rate"]
        if total == 100:
            return True
        else:
            return False

    def __is_not_exist_probability_keys(self,item_probability):
        keys = ["rate","prize"]
        for key in keys:
            if not item_probability.has_key(key):
                return key
        return False
    def __is_int(self,value):
        if isinstance( value,(int,long)):
            return True
        else:
            return False

    def __is_exist_event_masterid(self, event_id):
        model_mgr = self.getModelMgr()
        master = model_mgr.get_model(BattleEventMaster, event_id, using=settings.DB_READONLY)
        if master is None:
            return False
        return True

    def __is_exist_prizeid(self, prize_id):
        model_mgr = self.getModelMgr()
        master = model_mgr.get_model(PrizeMaster, prize_id, using=settings.DB_READONLY)
        if master is None:
            return False
        return True
        
    def __is_exist_cardid(self,card_id):
        model_mgr = self.getModelMgr()
        master = model_mgr.get_model(CardMaster, card_id, using=settings.DB_READONLY)
        if master is None:
            return False
        return True

    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

    def __check_prizedir(self, master_id, name, complete_prize_name):
        re_object = re.match(r'\[(\w+)\]', complete_prize_name)
        if re_object:
            rare = re_object.group(1)
            dir = name.upper().split('_')[1]
            if rare != dir:
                self.__raise_ModelEditValidError(master_id, (u'ピースのまとまり画像フォルダとコンプリート報酬のレア度が一致していません'))


def main(request):
    return Handler.run(request)
