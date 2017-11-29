# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from defines import Defines
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Gacha import RankingGachaMaster,\
    RankingGachaPlayLog
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.alert import AlertCode

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """ランキングガチャの全体履歴確認.
    """
    def process(self):
        
        model_mgr = self.getModelMgr()
        mid = str(self.request.get('_mid'))
        if mid and mid.isdigit():
            mid = int(mid)
        else:
            mid = None
        self.html_param['cur_mid'] = mid
        
        if mid:
            self.__put_log(mid)
        
        self.html_param['Defines'] = Defines
        self.html_param['url_view_rankinggacha_log'] = self.makeAppLinkUrlAdmin(UrlMaker.mgr_infomations('view_rankinggacha_log'))
        
        self.html_param['rankinggachamaster_list'] = model_mgr.get_mastermodel_all(RankingGachaMaster, order_by='id', using=backup_db)
        
        self.writeAppHtml('infomations/view_rankinggacha_log')
    
    def __put_log(self, mid):
        
        page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        filters = {
            'boxid' : mid,
        }
        num_max = RankingGachaPlayLog.count(filters, using=backup_db)
        if num_max < 1:
            self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.WARNING)
            return
        
        limit = 100
        offset = limit * page
        loglist = RankingGachaPlayLog.fetchValues(filters=filters, order_by='-id', limit=limit, offset=offset, using=backup_db)
        
        obj_loglist = []
        for logdata in loglist:
            url = UrlMaker.view_player(logdata.uid)
            obj_loglist.append({
                'uid' : logdata.uid,
                'url' : self.makeAppLinkUrlAdmin(url),
                'single' : logdata.point,
                'whole' : logdata.point_whole,
                'ctime' : logdata.ctime.strftime("%Y-%m-%d %H:%M:%S"),
            })
        self.html_param['loglist'] = obj_loglist
        
        url = UrlMaker.mgr_infomations('view_rankinggacha_log')
        url = OSAUtil.addQuery(url, '_mid', mid)
        self.putPagenation(url, page, num_max, limit)
    

def main(request):
    return Handler.run(request)
