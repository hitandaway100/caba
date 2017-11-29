# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubEventRankMaster
from platinumegg.app.cabaret.models.UserLog import UserLogCabaClubStore
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerDataWeekly
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util import db_util

class Command(BaseCommand):
    """経営システムの不具合修正."""

    def handle(self, *args, **options):
        print('=======================')
        print('fix_cabaclubrank_record')
        print('=======================')
        mid = 1
        BATCH_SIZE = 500

        model_mgr = ModelRequestMgr()
        self.all_clear_weekly(model_mgr)
        self.all_clear_eventrankmaster(model_mgr)

        max_uid = UserLogCabaClubStore.max_value('uid')
        for i in range(max_uid):
            uid = i+1;
            db_util.run_in_transaction(self.tr_write, uid, mid)
        
    def tr_write(self, uid, mid):
        # 限定的なので決め打ち
        str_date = '2016-10-03 12:00:00'
        
        model_mgr = ModelRequestMgr()

        rankmaster_id = CabaClubEventRankMaster.makeID(uid, mid)
        rank_model = model_mgr.get_model(CabaClubEventRankMaster, rankmaster_id)
        
        etime = BackendApi.to_cabaretclub_section_starttime(OSAUtil.get_now())
        weekly_id = CabaClubScorePlayerDataWeekly.makeID(uid, etime)
        player_weekly = model_mgr.get_model(CabaClubScorePlayerDataWeekly, weekly_id)

        logs = UserLogCabaClubStore.fetchValues(filters={'ctime__gte': str_date, 'uid': uid})
        if not logs:
            print('skip... uid:{}'.format(uid))
            return
        
        proceeds = sum([log.proceeds for log in logs])
        customer = sum([log.customer for log in logs])
        
        if rank_model:
            self.tr_update_cabaclubrank_proceeds(model_mgr, rankmaster_id, weekly_id, proceeds, customer)
        if player_weekly:
            self.tr_update_score_playdata_weekly(model_mgr, rankmaster_id, weekly_id, proceeds, customer)
        
        print('fix...  uid:{0} proceeds:{1} customer:{2}'.format(uid, proceeds, customer))
        model_mgr.write_all()
        model_mgr.write_end()

    def all_clear_eventrankmaster(self, model_mgr):
        player_weeklys = CabaClubEventRankMaster.fetchValues()
        for player_weekly in player_weeklys:
            player_weekly.proceeds = 0
            model_mgr.set_save(player_weekly)

        model_mgr.write_all()
        model_mgr.write_end()
        
    def all_clear_weekly(self, model_mgr):
        player_weeklys = CabaClubScorePlayerDataWeekly.fetchValues(filters={'week':201640})
        for player_weekly in player_weeklys:
            player_weekly.proceeds = 0
            player_weekly.customer = 0
            model_mgr.set_save(player_weekly)

        model_mgr.write_all()
        model_mgr.write_end()

    def tr_update_score_playdata_weekly(self, model_mgr, rankmaster_id, weekly_id, proceeds, customer):
        def forUpdateTask2(model, inserted):
            model.proceeds = proceeds
            model.customer = customer

        model_mgr.add_forupdate_task(CabaClubScorePlayerDataWeekly, weekly_id, forUpdateTask2)
        
    def tr_update_cabaclubrank_proceeds(self, model_mgr, rankmaster_id, weekly_id, proceeds, customer):
        """経営ランキングの売上を更新."""
        def forUpdateTask(model, inserted):
            model.proceeds = proceeds
        
        model_mgr.add_forupdate_task(CabaClubEventRankMaster, rankmaster_id, forUpdateTask)
        
