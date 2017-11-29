# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from defines import Defines
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.models.Memories import MemoriesMaster

class Handler(AdminHandler):
    """動画閲覧数(PC).
    """
    def process(self):
        
        movieviewlist = self.procPcMovieView()
        if not movieviewlist:
            self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.WARNING)
        self.html_param['movieviewlist'] = movieviewlist
        
        self.writeAppHtml('infomations/view_pcmovieview')
    
    def procPcMovieView(self):
        """動画閲覧回数(PC).
        """
        model_mgr = self.getModelMgr()
        
        movieviewlist = BackendApi.get_pcmovieview_list(model_mgr, using=settings.DB_READONLY)
        obj_movieviewlist = self.makeMovieViewObjList(movieviewlist)
        return obj_movieviewlist
    
    def makeMovieViewObjList(self, movieviewlist):
        """HTML埋め込み用のオブジェクトに.
        """
        model_mgr = self.getModelMgr()
        
        master_idlist = [movieview.id for movieview in movieviewlist]
        masters = BackendApi.get_model_dict(model_mgr, MemoriesMaster, master_idlist, using=settings.DB_READONLY)
        
        obj_movieviewlist = []
        for movieview in movieviewlist:
            obj = self.makeMovieViewObj(movieview, masters.get(movieview.id))
            obj_movieviewlist.append(obj)
        return obj_movieviewlist
    
    def makeMovieViewObj(self, movieview, memoriesmaster):
        """HTML用のオブジェクトにする.
        """
        if memoriesmaster:
            name = memoriesmaster.name
            text = memoriesmaster.text
        else:
            name = u'不明'
            text = u'不明'
        return {
            'id' : movieview.id,
            'name' : name,
            'text' : text,
            'cnt' : movieview.cnt,
        }

def main(request):
    return Handler.run(request)
