# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRequest
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.gacha import GachaUtil
from defines import Defines


class Handler(GachaHandler):
    """引抜実行アニメ(2ページ目以降).
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/gachaanimsub/')
        mid = args.getInt(0)
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        
        self.set_masterid(mid)
        
        v_player = self.getViewerPlayer()
        gachamaster = self.getGachaMaster()
        
        effectpath = GachaUtil.makeGachaEffectPath(gachamaster)
        dataUrl = self.makeAppLinkUrlEffectParamGet(GachaUtil.makeGachaDataUrl(v_player, gachamaster, page=page))
        self.appRedirectToEffect2(effectpath, dataUrl)
    

def main(request):
    return Handler.run(request)
