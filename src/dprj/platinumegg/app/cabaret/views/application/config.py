# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from defines import Defines


class Handler(AppHandler):
    """コンフィグページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        configdata = BackendApi.get_playerconfigdata(uid)
        scoutskip = BackendApi.get_scoutskip_flag(uid)
        
        if self.request.get(Defines.URLQUERY_FLAG) == '1':
            # 更新する.
            scoutskip = self.request.get('_scoutskip') == '1'
            autosell_rarity = self.request.get('_auto_sell') or -1
            configdata = BackendApi.save_playerconfigdata(uid, scoutskip, autosell_rarity)
            self.html_param['is_update'] = True
        
        self.html_param['playerconfigdata'] = Objects.playerconfigdata(configdata, scoutskip)
        
        self.writeAppHtml('config')

def main(request):
    return Handler.run(request)
