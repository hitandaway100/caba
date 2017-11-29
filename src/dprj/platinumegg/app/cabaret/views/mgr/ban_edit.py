# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.alert import AlertCode
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil

class Handler(AdminHandler):
    """アクセス禁止管理.
    """
    def process(self):
        
        args = self.getUrlArgs('/ban_edit/')
        ope = args.get(0)
        func = getattr(self, '_proc_%s' % ope, None)
        if func:
            func()
        
        model_mgr = self.getModelMgr()
        
        # 現在停止中のアカウント.
        modellist = BackendApi.get_playerlimitation_list(model_mgr, using=settings.DB_READONLY)
        uidlist = [model.id for model in modellist]
        players = BackendApi.get_players(self, uidlist, [], using=settings.DB_READONLY)
        
        obj_playerlist = []
        for player in players:
            url = UrlMaker.view_player(player.id)
            url_rem = OSAUtil.addQuery(UrlMaker.ban_edit('rem'), Defines.URLQUERY_ID, player.id)
            obj_playerlist.append({
                'id' : player.id,
                'dmmid' : player.dmmid,
                'url' : self.makeAppLinkUrlAdmin(url),
                'url_rem' : self.makeAppLinkUrlAdmin(url_rem),
            })
        self.html_param['playerlist'] = obj_playerlist
        
        self.html_param['url_add'] = self.makeAppLinkUrlAdmin(UrlMaker.ban_edit('add'))
        
        self.writeAppHtml('ban_edit')
    
    def __update_ban_flag(self, uidlist, flag):
        if not uidlist:
            self.putAlertToHtmlParam(u'ユーザIDが指定されていません', AlertCode.ERROR)
            return
        
        uidlist = list(set(uidlist))
        playerlst = BackendApi.get_players(self, uidlist, [], using=settings.DB_READONLY)
        if len(playerlst) != len(uidlist):
            self.putAlertToHtmlParam(u'存在しないIDが含まれています', AlertCode.ERROR)
            return False
        
        # 更新.
        BackendApi.update_player_ban(uidlist, flag)
        return True
    
    def _proc_add(self):
        """停止アカウントを追加.
        """
        str_uidlist = self.request.get(Defines.URLQUERY_ID)
        try:
            uidlist = [int(str_uid) for str_uid in str_uidlist.split(',') if str_uid]
        except:
            self.putAlertToHtmlParam(u'指定したユーザIDが不正です', AlertCode.ERROR)
            return
        
        if not self.__update_ban_flag(uidlist, True):
            return
        
        self.putAlertToHtmlParam(u'ユーザID[%s]をアクセス禁止リストに登録しました' % ','.join([str(uid) for uid in uidlist]), AlertCode.SUCCESS)
    
    def _proc_rem(self):
        """停止アカウントから除外.
        """
        str_uidlist = self.request.get(Defines.URLQUERY_ID)
        try:
            uidlist = [int(str_uid) for str_uid in str_uidlist.split(',') if str_uid]
        except:
            self.putAlertToHtmlParam(u'指定したユーザIDが不正です', AlertCode.ERROR)
            return
        
        if not self.__update_ban_flag(uidlist, False):
            return
        
        self.putAlertToHtmlParam(u'ユーザID[%s]をアクセスを許可しました' % ','.join([str(uid) for uid in uidlist]), AlertCode.SUCCESS)

def main(request):
    return Handler.run(request)
