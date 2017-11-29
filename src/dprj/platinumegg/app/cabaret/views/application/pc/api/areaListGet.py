# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings

class Handler(AppHandler):
    """エリア一覧.
    """
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        viewer_id = v_player.id
        
        arealist = BackendApi.get_playable_area_all(model_mgr, viewer_id, using=settings.DB_READONLY)
        playdata_dict = BackendApi.get_areaplaydata(model_mgr, viewer_id, [area.id for area in arealist], using=settings.DB_READONLY)
        
        self.json_result_param['arealist'] = [Objects.area(self, area, playdata_dict.get(area.id)) for area in arealist]
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
