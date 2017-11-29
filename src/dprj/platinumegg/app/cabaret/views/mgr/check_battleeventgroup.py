# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
import datetime
from platinumegg.app.cabaret.util.redisdb import RedisModel
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil


class Handler(AdminHandler):
    """バトルイベントのマッチングがちゃんと行われたかチェック.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        # 認証.
        if settings_sub.IS_DEV:
            return
        elif self.request.remote_addr.startswith('10.116.41.'):
            return
        self.response.set_status(404)
        raise CabaretError(u'NotFound!!', CabaretError.Code.NOT_AUTH)
    
    def send(self, status):
        self.response.set_status(status)
        self.response.send()
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        if config.endtime <= now:
            pass
        elif BackendApi.is_battleevent_battle_open(model_mgr, using=settings.DB_READONLY, now=now, do_check_emergency=False):
            # 開催中.
            if not config.isFirstDay(now) and not self.checkAggregateEnd(now):
                # ここが一番やばい.メンテモードにする.
                BackendApi.update_battleeventconfig(is_emergency=True)
                self.send(500)
                return
        else:
            bordertime = now + datetime.timedelta(seconds=1800)
            if BackendApi.is_battleevent_battle_open(model_mgr, using=settings.DB_READONLY, now=bordertime, do_check_emergency=False):
                # あと30分以内に開始する.
                if not self.checkAggregateEnd(bordertime):
                    # アラートだけ飛ばす.
                    self.send(500)
                    return
        
        self.send(200)
    
    def checkAggregateEnd(self, targettime):
        redisdb = RedisModel.getDB()
        ALREADY_KEY = "battleevent_aggregate:end"
        
        # 対象の日付(月).
        logintime = DateTimeUtil.toLoginTime(targettime)
        cdate = datetime.date(logintime.year, logintime.month, logintime.day)
        
        str_cdate_pre = redisdb.get(ALREADY_KEY)
        if str_cdate_pre:
            dt = DateTimeUtil.strToDateTime(str_cdate_pre, "%Y%m%d")
            cdate_pre = datetime.date(dt.year, dt.month, dt.day)
            if cdate_pre == cdate:
                # 集計が正常に終わっている.
                return True
        return False

def main(request):
    return Handler.run(request)
