# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from platinumegg.app.cabaret.kpi.operator import KpiOperator
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class Handler(AppHandler):
    """招待.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()
        
        invitemaster = BackendApi.get_current_invitemaster(model_mgr, using=settings.DB_READONLY)
        if invitemaster is None:
            raise CabaretError(u'招待キャンペーンは開催していません', CabaretError.Code.ILLEGAL_ARGS)
        
        # 招待したフレンド.
        invite_member = self.request.get("invite_member")
        if invite_member:
            str_dmmidlist = str(invite_member).split(',')
            KpiOperator().set_increment_invite_count(len(str_dmmidlist), OSAUtil.get_now()).save()
            self.addlog(u'invite_member:%d:%s' % (len(str_dmmidlist), invite_member))
        
        invite = BackendApi.get_invite(model_mgr, v_player.id, invitemaster.id, using=settings.DB_READONLY)
        
        self.html_param['invitecnt'] = invite.cnt
        
        url = OSAUtil.addQuery('invite:friends', 'callbackurl', self.makeAppLinkUrl(UrlMaker.invite(), add_frompage=False))
        url = OSAUtil.addQuery(url, 'body', u'招待報酬をGET')
        self.html_param['url_dmm_invite'] = url
        
        self.writeAppHtml('invite/invite')

def main(request):
    return Handler.run(request)
