# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Gacha import GachaMaster
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.models.PaymentEntry import GachaPaymentEntry
from defines import Defines
from platinumegg.lib.cache.localcache import localcache

class Handler(AdminHandler):
    """ガチャ課金額表示.
    """
    def process(self):
        
        mid = str(self.request.get('_mid') or '')
        if mid and mid.isdigit():
            mid = int(mid)
        else:
            mid = None
        
        masterlist = self.getGachaMasterList(mid)
        proceeds = []
        for master in masterlist:
            proceeds.append(self.makeProceeds(master))
        
        self.html_param['mid'] = mid
        self.html_param['proceeds'] = proceeds
        
        self.html_param['url_view_gacha_payment_proceeds'] = self.makeAppLinkUrlAdmin(UrlMaker.mgr_infomations('view_gacha_payment_proceeds'))
        
        self.putGachaMasterAll()
        
        self.writeAppHtml('infomations/view_gacha_payment_proceeds')
    
    def getGachaMasterList(self, mid):
        """集計対象のガチャのリストを取得.
        """
        if not mid:
            return []
        
        model_mgr = self.getModelMgr()
        master = BackendApi.get_gachamaster(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            return []
        
        if not master.stepid:
            return [master]
        
        masterlist = GachaMaster.fetchValues(filters={'stepid':master.stepid}, using=settings.DB_READONLY)
        masterlist.sort(key=lambda x:x.step)
        return masterlist
    
    def putGachaMasterAll(self):
        """選択可能なガチャマスターを全て埋め込む.
        """
        model_mgr = self.getModelMgr()
        obj_masterlist = []
        for master in model_mgr.get_mastermodel_all(GachaMaster, 'id', using=settings.DB_READONLY):
            if not (master.consumetype in Defines.GachaConsumeType.PAYMENT_TYPES and (not master.stepid or master.step==1)):
                continue
            
#            schedule = None
#            if master.schedule:
#                BackendApi.check_schedule(model_mgr, scheduleid, using, now)
            
            obj_masterlist.append({
                'id' : master.id,
                'name' : master.name,
                'stime' : '',
                'etime' : '',
            })
        self.html_param['masterlist'] = obj_masterlist
    
    def makeProceeds(self, master):
        """ガチャの課金情報を集計.
        """
        model_mgr = self.getModelMgr()
        appstime = DateTimeUtil.strToDateTime("20131224", "%Y%m%d")
        
        dest = {
            'id' : master.id,
            'name' : master.name,
        }
        schedulemaster = None
        if master.schedule:
            schedulemaster = BackendApi.get_schedule_master(model_mgr, master.schedule, using=settings.DB_READONLY)
        
        now = OSAUtil.get_now()
        if schedulemaster:
            stime = max(appstime, schedulemaster.stime)
            etime = min(now, schedulemaster.etime)
        else:
            stime = appstime
            etime = now
        
        table = {}
        filters = {
            'state' : PaymentData.Status.COMPLETED,
            'iid' : master.id,
        }
        cur_stime = stime
        
        useridset_total = set()
        count_total = 0
        
        while cur_stime < etime:
            
            filters['ctime__gte'] = cur_stime
            filters['ctime__lt'] = DateTimeUtil.toBaseTime(cur_stime+datetime.timedelta(days=1), 0)
            
            paymentlist = self.getPaymentFromCache(master.id, cur_stime, now)
            if paymentlist is None:
                paymentlist = GachaPaymentEntry.fetchValues(['uid', 'inum', 'price'], filters=filters, using=settings.DB_READONLY)
                self.setPaymentToCache(paymentlist, master.id, cur_stime, now)
            
            str_month = cur_stime.strftime("%Y%m")
            
            uidset = set([payment.uid for payment in paymentlist])
            cnt = len(paymentlist)
            
            monthdata = table[str_month] = table.get(str_month) or {'total':0, 'datalist':[], 'name':cur_stime.strftime(u"%Y年%m月"), 'count':0, 'uu':set()}
            monthdata['count'] += cnt
            monthdata['uu'] |= uidset
            useridset_total |= uidset
            count_total += cnt
            
            price = sum([payment.inum*payment.price for payment in paymentlist])
            monthdata['datalist'].append({
                'day' : cur_stime.day,
                'price' : price,
                'uu' : uidset,
                'count' : cnt,
            })
            monthdata['total'] += price
            
            cur_stime = filters['ctime__lt']
        
        monthlist = table.keys()
        monthlist.sort()
        dest['table'] = [table[month] for month in monthlist]
        dest['total'] = sum([data['total'] for data in dest['table']])
        dest['uu'] = useridset_total
        dest['count'] = count_total
        
        return dest
    
    def getPaymentFromCache(self, mid, stime, now):
        if DateTimeUtil.toBaseTime(now, 0) <= stime:
            return None
        client = localcache.Client()
        key = "view_gacha_payment_proceeds:%s:%s" % (mid, stime.strftime("%Y%m%d"))
        return client.get(key)
    
    def setPaymentToCache(self, paymentlist, mid, stime, now):
        if DateTimeUtil.toBaseTime(now, 0) <= stime:
            return None
        client = localcache.Client()
        key = "view_gacha_payment_proceeds:%s:%s" % (mid, stime.strftime("%Y%m%d"))
        client.set(key, paymentlist)
    

def main(request):
    return Handler.run(request)
