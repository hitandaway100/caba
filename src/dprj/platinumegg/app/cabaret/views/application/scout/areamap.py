# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from defines import Defines
import operator
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerExp

class Handler(AppHandler):
    """エリア一覧.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        viewer_id = v_player.id
        
        page_contentnum = Defines.SCOUTAREAMAP_CONTENTNUM_PER_PAGE
        
        # 遊べるエリア.
        arealist = BackendApi.get_playable_area_all(model_mgr, viewer_id, using=settings.DB_READONLY)
        if not arealist:
            raise CabaretError(u'エリアがありません', CabaretError.Code.INVALID_MASTERDATA)
        
        arealist.sort(key=operator.attrgetter('id'), reverse=True)
        playdata_dict = BackendApi.get_areaplaydata(model_mgr, viewer_id, [area.id for area in arealist], using=settings.DB_READONLY)
        
        # 現在ページ.
        contentnum = len(arealist)
        page_max = max(1, int((contentnum + page_contentnum - 1) / page_contentnum))
        page = 0
        try:
            page = min(page_max - 1, int(self.request.get(Defines.URLQUERY_PAGE, 0)))
        except:
            pass
        
        scoutidlist = []
        
        # 現在エリア.
        cur_area = arealist[0]
        self.html_param['area'] = Objects.area(self, cur_area, playdata_dict.get(cur_area.id))
        
        # 現在のスカウト.
        arr = BackendApi.get_scoutidlist_by_area(model_mgr, cur_area.id, using=settings.DB_READONLY)
        if not arr:
            raise CabaretError(u'エリアのスカウトがありません', CabaretError.Code.INVALID_MASTERDATA)
        arr.sort(reverse=True)
        scoutmasterdict = BackendApi.get_scout_dict(model_mgr, arr, using=settings.DB_READONLY)
        for scoutid in arr:
            master = scoutmasterdict.get(scoutid)
            if master and BackendApi.check_scout_playable(model_mgr, master, v_player, using=settings.DB_READONLY):
                scoutidlist.append(scoutid)
                break
        
        # ページのエリア.
        start = page * page_contentnum
        end = start + page_contentnum
        arealist = arealist[start:end]
        
        obj_arealist = []
        for area in arealist:
            if area.id != cur_area.id:
                arr = BackendApi.get_scoutidlist_by_area(model_mgr, area.id, using=settings.DB_READONLY)
                if not arr:
                    raise CabaretError(u'エリアのスカウトがありません', CabaretError.Code.INVALID_MASTERDATA)
                arr.sort(reverse=False)
                scoutidlist.append(arr[0])
            obj_arealist.append(Objects.area(self, area, playdata_dict.get(area.id)))
        
        obj_scout_dict = dict([(scout.area, Objects.scout(self, v_player, scout, 0, [])) for scout in BackendApi.get_scouts(model_mgr, scoutidlist, using=settings.DB_READONLY)])
        self.html_param['arealist'] = obj_arealist
        self.html_param['area_scout_dict'] = obj_scout_dict
        
        # ページング.
        url = UrlMaker.areamap()
        self.putPagenation(url, page, contentnum, page_contentnum)
        
        self.writeAppHtml('scout/areamap')
    
def main(request):
    return Handler.run(request)
