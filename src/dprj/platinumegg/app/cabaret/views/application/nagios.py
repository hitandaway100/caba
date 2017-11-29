# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.AppConfig import AppConfig
import settings
from platinumegg.lib.redis.client import Client
from platinumegg.lib.redis import config
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Happening import RaidPrizeDistributeQueue


class Handler(AdminHandler):
    """非対応ページ.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        # 認証.
        if settings_sub.IS_LOCAL:
            return
        elif self.request.remote_addr.startswith('10.116.41.'):
            return
        self.response.set_status(404)
        raise CabaretError(u'NotFound!!', CabaretError.Code.NOT_AUTH)
    
    def send(self, status):
        self.response.set_status(status)
        self.response.send()
    
    def checkDB(self, using):
        model = AppConfig.getByKey(AppConfig.SINGLE_ID, ['id'], using=using)
        if model is None:
            self.send(500)
            return False
        return True
    
    def checkRedis(self, db):
        redisdb = Client.get(db)
        
        redisdb.set('nagios_test', 1)
        
        v = redisdb.get('nagios_test')
        if str(v) != '1':
            self.send(500)
            return False
        return True
    
    def process(self):
        
        if self.request.get("raid") == '1':
            interval = 3600
            redisdb = Client.get(config.REDIS_DEFAULT)
            status = redisdb.get("check_RaidPrizeDistributeQueue")
            if status is None:
                backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)
                if 5000 < RaidPrizeDistributeQueue.count(using=backup_db):
                    status = "500"
                else:
                    status = "200"
                redisdb.set("check_RaidPrizeDistributeQueue", status)
                redisdb.expire("check_RaidPrizeDistributeQueue", interval)
            if status == "500":
                self.send("500")
                return
        else:
            # DB確認.
            if not self.checkDB(settings.DB_DEFAULT):
                return
            elif not self.checkDB(settings.DB_READONLY):
                return
            
            # Redis確認.
            elif not self.checkRedis(config.REDIS_DEFAULT):
                return
            elif not self.checkRedis(config.REDIS_CACHE):
                return
            elif not self.checkRedis(config.REDIS_LOG):
                return
            elif not self.checkRedis(config.REDIS_SESSION):
                return
        
        self.send(200)

def main(request):
    return Handler.run(request)
