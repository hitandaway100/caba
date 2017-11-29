# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneRecord,\
    PresentEveryoneLoginBonusMaster, PresentEveryoneMypageMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util

class Command(BaseCommand):
    """KPIの集計.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'create_presenteveryone_schedule'
        print '================================'
        
        DATE_FORMAT = "%Y%m%d"
        
        now = OSAUtil.get_now()
        today = DateTimeUtil.datetimeToDate(now)
        # 対象の日付.
        if args:
            target_dates = [DateTimeUtil.datetimeToDate(datetime.datetime.strptime(v, DATE_FORMAT), logintime=False) for v in args]
        else:
            start_date = DateTimeUtil.datetimeToDate(now, logintime=True) + datetime.timedelta(days=1)
            target_dates = [start_date + datetime.timedelta(days=i) for i in xrange(7)]
        
        # 既にあるかを検証.
        model_dict = dict([(model.date, model) for model in PresentEveryoneRecord.fetchValues(filters={'date__in':target_dates}, fetch_deleted=True)])
        
        save_list = []
        for target_date in target_dates:
            result = ''
            if target_date < today:
                print 'old'
            else:
                target_datetime = DateTimeUtil.dateToDateTime(target_date) + datetime.timedelta(seconds=Defines.DATE_CHANGE_TIME * 3600)
                # マスターデータを検索.
                filters = {
                    'e_date__gte' : target_date,
                }
                login_mid_list = [master.id for master in PresentEveryoneLoginBonusMaster.fetchValues(filters=filters) if master.s_date <= target_date]
                
                filters = {
                    'etime__gte' : target_datetime,
                }
                scheduleidlist = [schedule.id for schedule in ScheduleMaster.fetchValues(filters=filters) if DateTimeUtil.toLoginTime(schedule.stime) <= target_datetime]
                scheduleidlist.insert(0, 0)
                
                filters = {
                    'schedule__in' : scheduleidlist,
                }
                mypage_mid_list = [master.id for master in PresentEveryoneMypageMaster.fetchValues(filters=filters)]
                if model_dict.has_key(target_date):
                    model = model_dict[target_date]
                    
                    update = False
                    if today < target_date and (len(set(model.mid_loginbonus) - set(login_mid_list)) != 0 or len(set(login_mid_list) - set(model.mid_loginbonus)) != 0):
                        # 現在よりも後ならログインボーナスを受け取っていないからだいじょうぶ.
                        model.mid_loginbonus = list(set(login_mid_list))
                        update = True
                    
                    if len(set(model.mid_mypage) - set(mypage_mid_list)) != 0 or len(set(mypage_mid_list) - set(model.mid_mypage)) != 0:
                        model.mid_mypage = list(set(mypage_mid_list))
                        update = True
                    
                    if update:
                        save_list.append(model)
                        result = 'update'
                    else:
                        result = 'no change'
                else:
                    model = PresentEveryoneRecord()
                    model.date = target_date
                    model.mid_loginbonus = list(set(login_mid_list))
                    model.mid_mypage = list(set(mypage_mid_list))
                    save_list.append(model)
                    result = 'create'
            print '%s...%s' % (target_date.strftime("%Y%m%d"), result)
        
        # レコード作成.
        db_util.run_in_transaction(Command.tr_write, save_list, today).write_end()
        
        print '================================'
        print 'all done.'
    
    @staticmethod
    def tr_write(model_list, today):
        model_mgr = ModelRequestMgr()
        now = OSAUtil.get_now()
        for model in model_list:
            model.edittime = now
            model_mgr.set_save(model)
        
        # 削除.
        flag = False
        for model in PresentEveryoneRecord.fetchValues(filters={'date__lt':today}):
            model_mgr.set_delete(model)
            flag = True
        if flag:
            def writeEnd():
                model_mgr.get_mastermodel_all(PresentEveryoneRecord, fetch_deleted=True, reflesh=True)
            model_mgr.add_write_end_method(writeEnd)
        
        model_mgr.write_all()
        return model_mgr
    

