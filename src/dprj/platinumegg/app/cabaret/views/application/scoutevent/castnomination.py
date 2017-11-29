# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from defines import Defines
import settings_sub
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.item import ItemUtil


class Handler(ScoutHandler):
    """スカウトイベントキャスト指名.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 短冊情報.
        obj_tanzakulist = BackendApi.put_scoutevent_tanzakudata(self, uid)
        if not obj_tanzakulist:
            # 短冊が無いイベント.
            url = UrlMaker.scoutevent_top()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        obj_tanzaku = None
        
        # 短冊所持情報.
        tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(model_mgr, uid, mid, using=settings.DB_READONLY)
        current_cast_number = tanzakudata.current_cast if tanzakudata else -1
        if current_cast_number != -1:
            for obj in obj_tanzakulist:
                if obj['number'] == current_cast_number:
                    obj_tanzaku = obj
                    break
            
            # 一応データの不具合を防いでおく.
            if obj_tanzaku is None:
                if settings_sub.IS_DEV:
                    raise CabaretError(u'存在しないキャストを指名しています.{}'.format(current_cast_number))
                def tr():
                    model_mgr = ModelRequestMgr()
                    BackendApi.tr_scoutevent_nominate_cast(model_mgr, uid, mid, None)
                    model_mgr.write_all()
                    return model_mgr
                try:
                    db_util.run_in_transaction(tr).write_end()
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        pass
                    else:
                        raise
                url = UrlMaker.scouteventcastnomination()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        self.html_param['scoutevent_tanzaku'] = obj_tanzaku
        
        # 所持チップ数.
        scorerecord = BackendApi.get_scoutevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        self.html_param['scouteventscore'] = Objects.scoutevent_score(scorerecord)
        
        # トピック.
        self.putEventTopic(mid)
        
        # このページのURL.
        url = UrlMaker.scouteventcastnomination()
        self.html_param['url_self'] = self.makeAppLinkUrl(url)
        
        if obj_tanzaku:
            # 指名後.
            self.process_tip(eventmaster)
        else:
            # 指名前.
            self.process_tanzaku(eventmaster)
    
    def process_tip(self, eventmaster):
        """チップ投入(指名後).
        """
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        if self.request.method == 'POST':
            # 投入書き込み.
            str_tipnum = str(self.request.get(Defines.URLQUERY_NUMBER))
            if str_tipnum.isdigit():
                tipnum = int(str_tipnum)
                if 0 < tipnum:
                    
                    tanzakudata = BackendApi.get_scoutevent_tanzakucastdata(self.getModelMgr(), uid, eventmaster.id, using=settings.DB_READONLY)
                    
                    def tr(uid, eventmaster, tip):
                        model_mgr = ModelRequestMgr()
                        BackendApi.tr_scoutevent_populate_tip(model_mgr, uid, eventmaster, tip)
                        model_mgr.write_all()
                        return model_mgr
                    try:
                        db_util.run_in_transaction(tr, uid, eventmaster, tipnum).write_end()
                    except CabaretError, err:
                        if err.code == CabaretError.Code.ALREADY_RECEIVED:
                            pass
                        else:
                            raise
                    
                    # 結果ページ.
                    url = UrlMaker.scouteventtippopulatecomplete(tanzakudata.current_cast, tipnum)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
        
        scorerecord = BackendApi.get_scoutevent_scorerecord(self.getModelMgr(), eventmaster.id, uid, using=settings.DB_READONLY)
        self.html_param['tip_usenums'] = ItemUtil.makeUseNumListByList(scorerecord.tip if scorerecord else 0)
        
        self.writeScoutEventHTML('tip_populate', eventmaster)
    
    def process_tanzaku(self, eventmaster):
        """短冊投入(指名前).
        """
        if self.request.method == 'POST':
            # 指名書き込み.
            str_cast_number = str(self.request.get(Defines.URLQUERY_ID))
            if str_cast_number.isdigit():
                cast_number = int(str_cast_number)
                
                model_mgr = self.getModelMgr()
                v_player = self.getViewerPlayer()
                
                tanzakucastmaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, eventmaster.id, cast_number, using=settings.DB_READONLY)
                if tanzakucastmaster:
                    def tr(uid, eventid, tanzakucastmaster):
                        model_mgr = ModelRequestMgr()
                        BackendApi.tr_scoutevent_nominate_cast(model_mgr, uid, eventid, tanzakucastmaster)
                        model_mgr.write_all()
                        return model_mgr
                    try:
                        db_util.run_in_transaction(tr, v_player.id, eventmaster.id, tanzakucastmaster).write_end()
                    except CabaretError, err:
                        if err.code == CabaretError.Code.ALREADY_RECEIVED:
                            pass
                        else:
                            raise
                    
                    url = UrlMaker.scouteventcastnomination()
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
        
        self.writeScoutEventHTML('tanzaku_castnomination', eventmaster)

def main(request):
    return Handler.run(request)
