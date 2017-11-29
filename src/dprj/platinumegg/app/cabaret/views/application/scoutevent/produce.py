# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from platinumegg.app.cabaret.models.Player import PlayerRequest
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util


class Handler(ScoutHandler):
    """プロデュースプレゼントページ.
    引数
        書き込み用
            requestkey
            項目番号
        結果用
            項目番号
            投入した数
    表示するもの
        カード画像
        ハート所持数
        各項目
            名前
            次の報酬
            次の報酬までの個数
        書き込みURL
        書込結果
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        
        # スカウトイベントの設定.
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        if config.mid == 0 or config.present_endtime < now:
            # 交換が終了している.
            url = UrlMaker.scoutevent_top(config.mid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        eventid = config.mid
        eventmaster = BackendApi.get_scouteventmaster(model_mgr, eventid, using=settings.DB_READONLY)
        
        # 説明とランキングのリンク.
        self.putEventTopic(eventid, '')
        
        if self.request.method == 'POST':
            self.__procPost(eventmaster)
            if self.response.isEnd:
                return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        record = BackendApi.get_scoutevent_presentnums_record(model_mgr, eventid, uid, get_instance=True, using=settings.DB_READONLY)
        
        # プレイヤー情報.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # イベントデータ.
        obj_scoutevent = Objects.scouteventmaster(self, eventmaster, config)
        self.html_param['scoutevent'] = obj_scoutevent
        
        # ハート所持数.
        self.html_param['scoutevent_heartnum'] = record.point
        
        # 各項目.
        presentprizemasterlist = BackendApi.get_scoutevent_presentprizemaster_by_eventid(model_mgr, eventid, using=settings.DB_READONLY)
        obj_presentprizelist = []
        flag_allreceived = True
        for presentprizemaster in presentprizemasterlist:
            obj_presentprize = BackendApi.make_scoutevent_presentprizeinfo(self, presentprizemaster, record)
            obj_presentprizelist.append(obj_presentprize)
            if not obj_presentprize['all_received']:
                flag_allreceived = False
        self.html_param['scoutevent_presentprizelist'] = obj_presentprizelist
        self.html_param['scoutevent_flag_allreceived'] = flag_allreceived
        
        # 書き込み先URL.
        self.html_param['url_post'] = self.makeAppLinkUrl(UrlMaker.scouteventproduce())
        
        target_number = None
        try:
            target_number = int(self.request.get(Defines.URLQUERY_NUMBER))
        except:
            pass
        
        if target_number is not None and target_number == record.result_number:
            # 投入結果.
            pointprizemaster = BackendApi.get_scoutevent_presentprizemaster(model_mgr, eventid, record.result_number, using=settings.DB_READONLY)
            if pointprizemaster:
                prize_table = pointprizemaster.get_pointprizes(record.result_pointpre+1, record.result_pointpost)
                prizeinfo = None
                if prize_table:
                    prizeidlist = prize_table.values()[0]
                    prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
                    prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
                self.html_param['scoutevent_present_result'] = Objects.scoutevent_present_result(self, record.result_pointpost - record.result_pointpre, prizeinfo)
        
        self.writeScoutEventHTML('present', eventmaster)
    
    def __procPost(self, eventmaster):
        """投入書き込み.
        """
        # 引数取得.
        try:
            requestkey = self.request.get(Defines.URLQUERY_FLAG) or ''
            target_number = int(self.request.get(Defines.URLQUERY_NUMBER))
        except:
            return
        if not requestkey:
            return
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        eventid = eventmaster.id
        uid = v_player.id
        
        # 項目のマスター.
        presentprizemaster = BackendApi.get_scoutevent_presentprizemaster(model_mgr, eventid, target_number, using=settings.DB_READONLY)
        if presentprizemaster is None:
            return
        
        # 書き込み.
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, uid, presentprizemaster, requestkey)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                return
        
        # 結果ページへリダイレクト.
        url = UrlMaker.scouteventproduce()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_NUMBER, target_number)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(uid, presentprizemaster, requestkey):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_scoutevent_add_presentpointnum(model_mgr, uid, presentprizemaster, requestkey)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
