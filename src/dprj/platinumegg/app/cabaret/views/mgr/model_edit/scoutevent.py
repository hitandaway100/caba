# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventMaster
from platinumegg.app.cabaret.models.Text import TextMaster
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Memories import EventMovieMaster
import settings_sub
import os


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = ScoutEventMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )
        rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'ランキング報酬文言')
        pointprize_text = AppModelChoiceField(TextMaster, required=False, label=u'イベントポイント報酬文言')
        movie_op = AppModelChoiceField(EventMovieMaster, required=False, label=u'イベント動画ID')
        beginer_rankingprize_text = AppModelChoiceField(TextMaster, required=False, label=u'初心者ランキング報酬文言')
    
    def setting_property(self):
        self.MODEL_LABEL = u'スカウトイベント（管理）'
    
    def __valid_master(self, master):
        if not master.is_public:
            return
        
        model_mgr = self.getModelMgr()
        
        if not isinstance(master.rankingprizes, list):
            raise ModelEditValidError(u'ランキング報酬のJsonが壊れています.scoutevent=%d' % master.id)
        for data in master.rankingprizes:
            diff = set(['prize','rank_min','rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(u'ランキング報酬に想定外のデータが含まれています.scoutevent=%d' % master.id)
            self.checkPrize(master, data['prize'], u'ランキング報酬', u'scoutevent')
        
        master.beginer_rankingprizes = master.beginer_rankingprizes or []
        if not isinstance(master.beginer_rankingprizes, list):
            raise ModelEditValidError(u'新店舗ランキング報酬のJsonが壊れています.scoutevent=%d' % master.id)
        for data in master.beginer_rankingprizes:
            diff = set(['prize','rank_min','rank_max']) - set(data.keys())
            if diff:
                raise ModelEditValidError(u'新店舗ランキング報酬に想定外のデータが含まれています.scoutevent=%d' % master.id)
            self.checkPrize(master, data['prize'], u'新店舗ランキング報酬', u'scoutevent')
        
        if not isinstance(master.pointprizes, (dict, list)):
            raise ModelEditValidError(u'ポイント達成報酬のJsonが壊れています.scoutevent=%d' % master.id)
        for prizeidlist in master.get_pointprizes().values():
            self.checkPrize(master, prizeidlist, u'ポイント達成報酬', u'scoutevent')
        
        midlist = dict(master.specialcard).keys()
        if len(midlist) != len(master.specialcard):
            raise ModelEditValidError(u'ご指名キャストが重複しています.scoutevent=%d' % master.id)
        elif len(CardMaster.getByKey(midlist)) != len(midlist):
            raise ModelEditValidError(u'存在しないキャストがご指名されています.scoutevent=%d' % master.id)
        
        if master.movie_op:
            moviemaster = BackendApi.get_eventmovie_master(model_mgr, master.movie_op)
            if moviemaster is None:
                raise ModelEditValidError(u'存在しない動画が設定されています.scoutevent=%d' % master.id)

        if not self.__is_exist_file(master.lovetime_starimgon):
            raise ModelEditValidError(u'「星の取得画像」に存在しない画像が設定されています.scoutevent=%d' % master.id)
        if not self.__is_exist_file(master.lovetime_starimgoff):
            raise ModelEditValidError(u'「星の身取得画像」に存在しない画像が設定されています.scoutevent=%d' % master.id)
    
    def __is_exist_file(self,path):
        if not path:
            return True

        full_path = settings_sub.STATIC_DOC_ROOT + "/img/sp/large/item/scevent/" + path
        return os.path.isfile(full_path)

    def valid_insert(self, master):
        self.__valid_master(master)
    
    def valid_update(self, master):
        self.__valid_master(master)

def main(request):
    return Handler.run(request)
