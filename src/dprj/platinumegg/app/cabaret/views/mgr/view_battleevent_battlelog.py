# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventBattleLog
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util.alert import AlertCode

class Handler(AdminHandler):
    """バトルイベントバトル履歴確認.
    """
    def process(self):
        
        uid = self.__get_uid()
        
        obj_battleloglist = []
        if uid:
            page = int(self.request.get('_page') or 0)
            
            target_oid = self.__get_oid()
            
            PAGE_CONTENT_NUM_MAX = 100
            if target_oid:
                modellist = [model for model in BattleEventBattleLog.fetchValues(filters={'uid':uid}, order_by='-ctime', using=settings.DB_READONLY) if model.data['oid'] == target_oid]
                lognum = len(modellist)
                page_max = int((lognum + PAGE_CONTENT_NUM_MAX - 1) / PAGE_CONTENT_NUM_MAX)
                
                offset = page * PAGE_CONTENT_NUM_MAX
                modellist = modellist[offset:(offset + PAGE_CONTENT_NUM_MAX)]
            else:
                lognum = BattleEventBattleLog.count(filters={'uid':uid}, using=settings.DB_READONLY)
                page_max = int((lognum + PAGE_CONTENT_NUM_MAX - 1) / PAGE_CONTENT_NUM_MAX)
                
                offset = page * PAGE_CONTENT_NUM_MAX
                modellist = BattleEventBattleLog.fetchValues(filters={'uid':uid}, order_by='-ctime', limit=PAGE_CONTENT_NUM_MAX, offset=offset, using=settings.DB_READONLY)
            
            oidlist = list(set([model.data['oid'] for model in modellist]))
            playerdict = dict([(player.id, player) for player in BackendApi.get_players(self, oidlist, [], using=settings.DB_READONLY)])
            persons = BackendApi.get_dmmplayers(self, playerdict.values(), using=settings.DB_READONLY)
            
            for model in modellist:
                obj_battlelog = {
                    'is_win' : model.data['result'] == Defines.BattleResultCode.WIN,
                    'ctime' : model.ctime.strftime("%Y/%m/%d %H:%M:%S"),
                }
                o_player = playerdict.get(model.data['oid'])
                if o_player:
                    obj_o_player = Objects.player(self, o_player, persons.get(o_player.dmmid))
                    obj_o_player['url'] = self.makeAppLinkUrlAdmin(UrlMaker.view_player(o_player.id))
                    obj_battlelog['o_player'] = obj_o_player
                obj_battlelog.update(model.data)
                obj_battleloglist.append(obj_battlelog)
            
            if not obj_battleloglist:
                self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.INFO)
            
            url = UrlMaker.view_battleevent_battlelog()
            url = OSAUtil.addQuery(url, '_serchtype', self.html_param['_serchtype'])
            url = OSAUtil.addQuery(url, '_value', self.html_param['_value'])
            url = OSAUtil.addQuery(url, '_serchtype_o', self.html_param['_serchtype_o'])
            url = OSAUtil.addQuery(url, '_value_o', self.html_param['_value_o'])
            def __makePage(index):
                return {
                    'num':index,
                    'url':self.makeAppLinkUrlAdmin(OSAUtil.addQuery(url, '_page', index-1)),
                }
            pagination_data = {
                'page_list':[__makePage(p) for p in xrange(1, page_max+1)],
                'now_page':__makePage(page+1),
                'has_next':False,
                'has_prev':False,
            }
            if page < page_max:
                pagination_data['next_page'] = __makePage(page + 1)
                pagination_data['has_next'] = True
            if 1 < page:
                pagination_data['prev_page'] = __makePage(page - 1)
                pagination_data['has_prev'] = True
            self.html_param['pagination'] = pagination_data
        
        self.html_param['battleloglist'] = obj_battleloglist
        
        self.html_param['url_view_battleevent_battlelog'] = self.makeAppLinkUrlAdmin(UrlMaker.view_battleevent_battlelog())
        
        self.writeAppHtml('infomations/view_battleevent/battlelog')
    
    def __get_userid(self, serchtype, v):
        uid = None
        if serchtype == 'uid':
            uid = str(v)
            if uid and uid.isdigit():
                uid = int(uid)
            else:
                uid = None
        elif serchtype == 'dmmid':
            dmmid = str(v)
            uid = BackendApi.dmmid_to_appuid(self, [dmmid], using=settings.DB_READONLY).get(dmmid)
        return uid
    
    def __get_uid(self):
        serchtype = self.request.get('_serchtype')
        v = self.request.get('_value')
        
        self.html_param['_serchtype'] = serchtype
        self.html_param['_value'] = v
        
        return self.__get_userid(serchtype, v)
    
    def __get_oid(self):
        serchtype = self.request.get('_serchtype_o')
        v = self.request.get('_value_o')
        
        self.html_param['_serchtype_o'] = serchtype
        self.html_param['_value_o'] = v
        
        return self.__get_userid(serchtype, v)

def main(request):
    return Handler.run(request)
