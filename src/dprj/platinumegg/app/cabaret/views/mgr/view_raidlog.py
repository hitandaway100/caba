# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Happening import RaidMaster,\
    RaidLog, Raid, Happening
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventMaster
from platinumegg.app.cabaret.util.happening import RaidBoss, HappeningUtil

class Handler(AdminHandler):
    """レイド情報確認.
    """
    def process(self):
        
        def to_i(v):
            if str(v).isdigit():
                return int(v)
            else:
                return None
        
        serchtype = self.request.get('_serchtype')
        value = self.request.get('_value')
        page = (to_i(self.request.get('_page')) or 0)
        
        model_mgr = self.getModelMgr()
        raid_all = dict([(master.id, master) for master in model_mgr.get_mastermodel_all(RaidMaster, fetch_deleted=True, using=settings.DB_READONLY)])
        event_all = dict([(master.id, master) for master in model_mgr.get_mastermodel_all(RaidEventMaster, fetch_deleted=True, using=settings.DB_READONLY)])
        
        uid = None
        if serchtype == 'uid':
            uid = to_i(value)
        elif serchtype == 'dmmid':
            uid = BackendApi.dmmid_to_appuid(self, [value], using=settings.DB_READONLY).get(value)
        
        if uid:
            PAGE_CONTENT_NUM = 100
            
            filters = {
                'uid' : uid,
            }
            nummax = RaidLog.count(filters, using=settings.DB_READONLY)
            page_max = (nummax + PAGE_CONTENT_NUM - 1) / PAGE_CONTENT_NUM
            
            offset = page * PAGE_CONTENT_NUM
            raidloglist = RaidLog.fetchValues(filters=filters, order_by='-ctime', limit=PAGE_CONTENT_NUM, offset=offset, using=settings.DB_READONLY)
            raididlist = [raidlog.raidid for raidlog in raidloglist]
            recorddict = BackendApi.get_model_dict(model_mgr, Raid, raididlist, using=settings.DB_READONLY)
            happeningdict = BackendApi.get_model_dict(model_mgr, Happening, raididlist, using=settings.DB_READONLY)
            
            raidlist = []
            for raidlog in raidloglist:
                happening = happeningdict.get(raidlog.raidid)
                record = recorddict.get(raidlog.raidid)
                raidboss = None
                eventmaster = None
                
                if record and happening:
                    master = raid_all.get(record.mid)
                    if master:
                        raidevent_id = HappeningUtil.get_raideventid(happening.event)
                        eventmaster = event_all.get(raidevent_id)
                        eventraidmaster = None
                        if eventmaster:
                            eventraidmaster = BackendApi.get_raidevent_raidmaster(model_mgr, raidevent_id, master.id)
                        raidboss = RaidBoss(record, master, eventraidmaster)
                
                if raidboss:
                    point = 0
                    eventdata = None
                    is_champagne_call = False
                    champagne_num_add = 0
                    champagne_num_post = 0
                    material = 0
                    if eventmaster:
                        if raidboss.hp < 1:
                            fastbonusdata = BackendApi.get_raidevent_fastbonusdata(eventmaster, raidboss, happening.etime)
                            rate = 1
                            if fastbonusdata:
                                rate = fastbonusdata['rate']
                            if happening.oid == uid:
                                point += raidboss.get_owner_eventpoint()
                            else:
                                point += raidboss.getHelpEventPoints(uid).get(uid, 0)
                            if uid in raidboss.getMVPList():
                                point += raidboss.get_mvp_eventpoint()
                            point = point * rate
                        
                        record = raidboss.getDamageRecord(uid)
                        is_champagne_call = record.champagne
                        champagne_num_add = record.champagne_num_add
                        champagne_num_post = record.champagne_num_post
                        material = record.material_num
                        
                        eventdata = {
                            'id' : eventmaster.id,
                            'name' : eventmaster.name,
                        }
                    
                    raidlist.append({
                        'id' : raidboss.id,
                        'mid' : raidboss.master.id,
                        'name' : '%s%s' % (raidboss.master.name, u'[ｲﾍﾞ]' if raidboss.raideventraidmaster else ''),
                        'level' : raidboss.raid.level,
                        'ctime' : DateTimeUtil.dateTimeToStr(raidboss.raid.ctime),
                        'url' : self.makeAppLinkUrlAdmin(UrlMaker.view_raid(raidboss.id)),
                        'point' : point,
                        'eventdata' : eventdata,
                        'is_champagne_call' : is_champagne_call,
                        'champagne_num_add' : champagne_num_add,
                        'champagne_num_post' : champagne_num_post,
                        'material' : material,
                    })
                else:
                    raidlist.append({
                        'id' : raidlog.raidid,
                        'mid' : record.mid if record else 0,
                        'name' : master.name if master else u'不明',
                        'level' : record.level if record else 0,
                        'ctime' : DateTimeUtil.dateTimeToStr(record.ctime) if record else u'不明',
                        'url' : None,
                        'point' : 0,
                        'eventdata' : None,
                    })
            
            url = UrlMaker.view_raidlog()
            url = OSAUtil.addQuery(url, '_serchtype', serchtype)
            url = OSAUtil.addQuery(url, '_value', value)
            
            def __makePage(index):
                return {
                    'num':index,
                    'url':self.makeAppLinkUrlAdmin(OSAUtil.addQuery(url, '_page', index-1)),
                }
            pagination_data = {
                'page_list':[__makePage(p) for p in xrange(1, page_max + 1)],
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
            
            self.html_param['raidlist'] = raidlist
        
        self.html_param['serchtype'] = serchtype
        self.html_param['value'] = value
        
        self.html_param['url_view_raidlog'] = self.makeAppLinkUrlAdmin(UrlMaker.view_raidlog())
        
        self.writeAppHtml('infomations/view_raid/log')

def main(request):
    return Handler.run(request)
