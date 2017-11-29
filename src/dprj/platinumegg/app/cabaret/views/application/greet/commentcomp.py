# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerGachaPt
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AppHandler):
    """あいさつコメント完了.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt]
    
    def process(self):
        
        args = self.getUrlArgs('/greet_comment_comp/')
        oid = args.get(0, None)
        errcode = args.get(1, None)
        point_pre = args.get(2, None)
        point_post = args.get(3, None)
        
        if not (str(oid).isdigit() and str(errcode).isdigit() and str(point_pre).isdigit() and str(point_post).isdigit()):
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        oid = int(args.get(0, None))
        errcode = int(args.get(1, None))
        point_pre = int(args.get(2, None))
        point_post = int(args.get(3, None))
        
        o_player = BackendApi.get_players(self, [oid], [], using=settings.DB_READONLY)
        if o_player:
            o_player = o_player[0]
        else:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        persons = BackendApi.get_dmmplayers(self, [o_player], using=settings.DB_READONLY)
        self.html_param['person'] = Objects.person(self, o_player, persons.get(o_player.dmmid))
        
        is_overlimit = False
        is_duplicate = False
        if errcode == CabaretError.Code.OK:
            pass
        elif errcode == CabaretError.Code.ALREADY_RECEIVED:
            is_duplicate = True
        elif errcode == CabaretError.Code.OVER_LIMIT:
            is_overlimit = True
        
        self.html_param['is_duplicate'] = is_duplicate
        self.html_param['is_overlimit'] = is_overlimit
        
        self.html_param['gacha_pt_pre'] = point_pre
        self.html_param['gacha_pt_post'] = point_post
        self.html_param['gacha_pt_add'] = point_post - point_pre
        
        url = UrlMaker.profile(oid)
        self.html_param['url_profile'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('greetcommentcomp')

def main(request):
    return Handler.run(request)
