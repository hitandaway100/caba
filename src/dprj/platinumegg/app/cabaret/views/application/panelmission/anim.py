# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.panelmission.base import PanelMissionHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(PanelMissionHandler):
    """パネルミッション演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        using = settings.DB_READONLY
        
        args = self.getUrlArgs('/panelmissionanim/')
        panel = args.getInt(0)
        
        # パネルのマスターデータ.
        panelmaster = None
        if panel:
            panelmaster = BackendApi.get_panelmission_panelmaster(model_mgr, panel, using=using)
        if panelmaster is None:
            raise CabaretError(u'存在しないパネルです', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 進行情報.
        panelplaydata = BackendApi.get_panelmission_data(model_mgr, uid, panel, using=using, get_instance=False)
        if panelplaydata is None:
            raise CabaretError(u'未プレイのパネルです', CabaretError.Code.ILLEGAL_ARGS)
        
        dataUrl = self.makeAppLinkUrlEffectParamGet('panelmission/%d' % panelmaster.id)
        self.appRedirectToEffect2('%s/effect2.html' % panelmaster.effectname, dataUrl)

def main(request):
    return Handler.run(request)

