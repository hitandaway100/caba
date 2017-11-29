# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerGachaPt
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
import settings_sub
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.lib.platform.api.objects import InspectionPostRequestData, InspectionData
from platinumegg.lib.strutil import StrUtil


class Handler(AppHandler):
    """あいさつ完了.
    """
    KEY_GREET_COMMENT = u'comment'
    KEY_GREET_TEXTID = u'textid'
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt]
    
    def process(self):
        
        args = self.getUrlArgs('/greet_complete/')
        oid = args.get(0, None)
        errcode = args.get(1, None)
        point_pre = args.get(2, None)
        point_post = args.get(3, None)
        logid = args.get(4, None)
        
        if not (str(oid).isdigit() and str(errcode).isdigit() and str(point_pre).isdigit() and str(point_post).isdigit()):
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        oid = int(args.get(0, None))
        errcode = int(args.get(1, None))
        point_pre = int(args.get(2, None))
        point_post = int(args.get(3, None))
        if logid:
            logid = int(logid)
        
        o_player = BackendApi.get_players(self, [oid], [], using=settings.DB_READONLY)
        if o_player:
            o_player = o_player[0]
        else:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        if not logid:
            url = UrlMaker.profile(o_player.id)
            url = self.makeAppLinkUrlRedirect(url)
            self.appRedirect(url)
            return
        
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
        
        url = UrlMaker.greet_complete(o_player.id, errcode, point_pre, point_post, logid)
        self.html_param['url_self'] = self.makeAppLinkUrl(url)

        errtext = False
        comment = u''
        if self.request.method == 'POST':
            comment = self.request.get(self.KEY_GREET_COMMENT)
            
            if comment == u'':
                errtext = True
            
            # コメントのバイト数で比較
            if StrUtil.getByteLength(comment) > (Defines.GREET_COMMENT_TEXT_MAX*2):
                errtext = True
            
            if not errtext and self.is_pc:
                # JS API経由でtextidを取得済み
                textid = self.request.get(self.KEY_GREET_TEXTID)
            elif not errtext:
                data = InspectionPostRequestData()
                data.data = comment
                request = self.osa_util.makeApiRequest(ApiNames.InspectionPost, data)
                self.addAppApiRequest('inspection_start', request)
                
                ret_data = self.execute_api()
                
                result = ret_data['inspection_start'].get()
                if isinstance(result, InspectionData):
                    textid = result.textId
                else:
                    if not settings_sub.IS_LOCAL:
                        errtext = True
                    else:
                        textid = '0000'
            
            if not errtext:
                v_player = self.getViewerPlayer()
                
                point_pre = v_player.gachapt
                point_post = v_player.gachapt
                
                model_mgr = self.getModelMgr()
                is_friend = BackendApi.check_friend(v_player.id, o_player.id, model_mgr, using=settings.DB_READONLY)
                
                try:
                    model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, o_player.id, is_friend, logid, textid)
                    model_mgr.write_end()
                    playergachapt = model_mgr.get_wrote_model(PlayerGachaPt, v_player.id)
                    if playergachapt:
                        point_post = playergachapt.gachapt
                except CabaretError,e:
                    if e.code in (CabaretError.Code.NOT_DATA):
                        url = UrlMaker.greet(o_player.id)
                        url = self.makeAppLinkUrlRedirect(url)
                        self.appRedirect(url)
                        return
                    else:
                        raise
                
                errcode = 0
                if point_pre >= point_post:
                    errcode = CabaretError.Code.ALREADY_RECEIVED
                url = UrlMaker.greet_comment_comp(o_player.id, errcode, point_pre, point_post)
                url = self.makeAppLinkUrlRedirect(url)
                self.appRedirect(url)
                return
            
        self.html_param['is_errtext'] = errtext
        self.html_param['text_comment'] = comment
        self.html_param['comment_max'] = Defines.GREET_COMMENT_TEXT_MAX
        self.html_param['logid'] = logid
        
        self.writeAppHtml('greetingcomp')
    
    @staticmethod
    def tr_write(uid, oid, is_friend, logid, textid):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_greet_comment(model_mgr, uid, oid, is_friend, logid, textid)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
