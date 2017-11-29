# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.models.PresentEveryone import PresentEveryoneReceiveMypage
from defines import Defines
from platinumegg.app.cabaret.models.Item import Item
from platinumegg.app.cabaret.models.Present import Present
import settings_sub
from platinumegg.app.cabaret.models.Player import PlayerDeck

class Command(BaseCommand):
    """誤配布したプレゼントを修復.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'recov_present'
        print '================================'
        
        IS_TEST = args[0] != 'write'
        # 問題の発生時間.
#        targetstime = DateTimeUtil.strToDateTime("2014-06-13 00:00:00", "%Y-%m-%d %H:%M:%S")
        print 'TEST_MODE=%s' % IS_TEST
        
        """間違えて配った新店舗ランキング報酬を削除.
        とりあえずredisだけ.MySQLは直接消す.
        """
        targetstime = DateTimeUtil.strToDateTime("2014-11-18 15:00:00", "%Y-%m-%d %H:%M:%S")
        for present in Present.fetchValues(['id','toid', 'itype'], {'textid':144, 'ctime__gte':targetstime}):
            BackendApi.remove_present(present.toid, present.id, present.itype)
            print 'delete...(%s,%s,%s)' % (present.toid, present.id, present.itype)
        
#        worked = (660,1661,3581,3720,8126,9614,16668,17376,17509,21214,22047,24504,24561,28933,29917,30368,32027,32498,32769,33609,34236,34841,40884,41124,42399,43762,44215,48391,48677,49798,50201,51676,52670,53295,55290,55910,56477,56838,57510,58601,59730,60412,63282,67219,69693,73282,73500,75072,78939,82382,83309,85689,86435,88635,90980,94654,99140,99325,103059,105616,105626,105964,111016,112823,114409,120378,121419,134001,134259,135012,136129,139024,139036,139055,139057,139066,139088,139115,139116,139121,139151,139159,139162,139200,139323,139331,139332,139335,139364,139367,139386,139451,139453,139523,139540,139582,139583,139606,139610,139618,139625,139627,139675,139694,139703,139721,139722,139727,139733,139746,139815,139820,139850,139854,139857,139871,139892,139912,139932,139970,140006,140047,140054,140061,140070,140076,140113,140117,140160,140175,140189,140224,140233,140240,140266,140328,140329,140363,140366,140412,140418,140419,140453,140459,140475,140493,140503,140518,140557,140612,140618,140644,140646,140666,140671,140692,140695,140735,140739,140743,140775,140792,140809,140842,140871,140884,140888,140892,140893,140897,140939,140985,140986,140993,141006,141015,141030,141051,141064,141074,141109,141130,141139,141161,141175,141182,141197,141203,141211,141221,141225,141227,141229,141249,141284,141292,141332,141346,141351,141368,141400,141414,141444,141462,141533,141541,141542,141578,141583,141585,141604,141703,141708,141719,141736,141754,141762,141783,141792,141794,141795,141796,141810,141817,141818,141834,141844,141867,141891,141893,141901)
#        
#        if settings_sub.IS_DEV:
#            LIMIT = 1
#        else:
#            LIMIT = 500
#        itemid = Defines.ItemEffect.CARD_BOX_EXPANSION
#        
#        """
#        ・全プレID:10を受け取ったユーザーのアイテム所持数を1個減らす。減らせない場合はプレゼントを削除。
#        ・2014-06-13 00:00:00以降に全プレID:9を受け取ったユーザーのアイテム所持数を4個増やす。
#        """
#        
#        # 全プレID:10を受け取ったユーザーのアイテム所持数を1個減らす。減らせない場合はプレゼントを削除.
#        offset = 0
#        filters = {
#            'mid' : 10,
#        }
#        
#        unable_nums = {}
#        
#        print 'start ID=10'
#        while True:
#            modellist = PresentEveryoneReceiveMypage.fetchValues(filters=filters, order_by='id', limit=LIMIT, offset=offset)
#            if not modellist:
#                break
#            
#            delete_num = 0
#            for model in modellist:
#                uid = model.uid
#                
#                # 所持数確認.
#                item = Item.getByKey(Item.makeID(uid, itemid))
#                if item and 0 < item.vnum:
#                    if not IS_TEST:
#                        def tr_item(modelid, uid, itemid):
#                            # 所持数を減らす.
#                            model_mgr = ModelRequestMgr()
#                            BackendApi.tr_add_item(model_mgr, uid, itemid, -1)
#                            
#                            # 受け取りフラグを消す.
#                            model = PresentEveryoneReceiveMypage.getByKeyForUpdate(modelid)
#                            model_mgr.set_delete(model)
#                            
#                            model_mgr.write_all()
#                            return model_mgr
#                        db_util.run_in_transaction(tr_item, model.id, uid, itemid).write_end()
#                        delete_num += 1
#                    print '%s=>item' % uid
#                else:
#                    # プレゼントを探す.
#                    present = Present.getValues(filters={'toid':uid,'itype':Defines.ItemType.ITEM,'ivalue':itemid,'inum':1})
#                    if present is None:
#                        # ここに来るのは受取済みで使用済み.
#                        unable_nums[uid] = 1
#                        print 'unable %s' % uid
#                    else:
#                        if not IS_TEST:
#                            def tr_present(modelid, uid, presentid):
#                                model_mgr = ModelRequestMgr()
#                                
#                                # プレゼントを消す.
#                                present = Present.getByKeyForUpdate(presentid)
#                                model_mgr.set_delete(present)
#                                
#                                # 受け取りフラグを消す.
#                                model = PresentEveryoneReceiveMypage.getByKeyForUpdate(modelid)
#                                model_mgr.set_delete(model)
#                                
#                                def writeEnd():
#                                    BackendApi.remove_present(uid, presentid)
#                                model_mgr.add_write_end_method(writeEnd)
#                                
#                                model_mgr.write_all()
#                                return model_mgr
#                            db_util.run_in_transaction(tr_present, model.id, uid, present.id).write_end()
#                            delete_num += 1
#                        print '%s=>present %d' % (uid, present.id)
#            offset += LIMIT - delete_num
            
        
#        # 2014-06-13 00:00:00以降に全プレID:9を受け取ったユーザーのアイテム所持数を4個増やす.
#        offset = 0
#        filters = {
#            'mid' : 9,
#            'rtime__gte' : targetstime,
#        }
#        print 'start ID=9'
#        while True:
#            modellist = PresentEveryoneReceiveMypage.fetchValues(filters=filters, order_by='id', limit=LIMIT, offset=offset)
#            offset += LIMIT
#            if not modellist:
#                break
#            
#            uidlist = list(set([model.uid for model in modellist]))
#            for uid in uidlist:
#                add_num = 4 - unable_nums.get(uid, 0)
#                if not IS_TEST:
#                    def tr(uid, itemid, add_num):
#                        model_mgr = ModelRequestMgr()
#                        BackendApi.tr_add_item(model_mgr, uid, itemid, add_num)
#                        model_mgr.write_all()
#                        return model_mgr
#                    db_util.run_in_transaction(tr, uid, itemid, add_num).write_end()
#                print 'add item:%s=>%d' % (uid, add_num)
#        
#        # 2014-05-23 16:00:00以降に全プレID:7を受け取ったユーザーのアイテム所持数を1個減らす.減らせない場合はプレゼントを消す.
#        targetstime = DateTimeUtil.strToDateTime("2014-05-23 16:00:00", "%Y-%m-%d %H:%M:%S")
#        
#        offset = 0
#        filters = {
#            'mid' : 7,
#            'rtime__gte' : targetstime,
#        }
#        print 'start ID=7'
#        while True:
#            modellist = PresentEveryoneReceiveMypage.fetchValues(filters=filters, order_by='id', limit=LIMIT, offset=offset)
#            if not modellist:
#                break
#            
#            delete_num = 0
#            for model in modellist:
#                uid = model.uid
#                if uid in worked:
#                    # 処理済み.
#                    continue
#                
#                # 所持数確認.
#                item = Item.getByKey(Item.makeID(uid, itemid))
#                if item and 0 < item.vnum:
#                    if not IS_TEST:
#                        def tr_item(modelid, uid, itemid):
#                            # 所持数を減らす.
#                            model_mgr = ModelRequestMgr()
#                            BackendApi.tr_add_item(model_mgr, uid, itemid, -1)
#                            
#                            # 受け取りフラグを消す.
#                            model = PresentEveryoneReceiveMypage.getByKeyForUpdate(modelid)
#                            model_mgr.set_delete(model)
#                            
#                            model_mgr.write_all()
#                            return model_mgr
#                        db_util.run_in_transaction(tr_item, model.id, uid, itemid).write_end()
#                        delete_num += 1
#                    print '%s=>item' % uid
#                else:
#                    # プレゼントを探す.
#                    present = Present.getValues(filters={'toid':uid,'itype':Defines.ItemType.ITEM,'ivalue':itemid,'inum':1})
#                    if present is None:
#                        # ボックス上限を減らす.
#                        if not IS_TEST:
#                            def tr_player(modelid, uid):
#                                model_mgr = ModelRequestMgr()
#                                
#                                player = PlayerDeck.getByKeyForUpdate(uid)
#                                player.cardlimititem = max(0, player.cardlimititem - 20)
#                                model_mgr.set_save(player)
#                                
#                                # 受け取りフラグを消す.
#                                model = PresentEveryoneReceiveMypage.getByKeyForUpdate(modelid)
#                                model_mgr.set_delete(model)
#                                
#                                model_mgr.write_all()
#                                return model_mgr
#                            db_util.run_in_transaction(tr_player, model.id, uid).write_end()
#                            delete_num += 1
#                        print 'box %s' % uid
#                    else:
#                        if not IS_TEST:
#                            def tr_present(modelid, uid, presentid):
#                                model_mgr = ModelRequestMgr()
#                                
#                                # プレゼントを消す.
#                                present = Present.getByKeyForUpdate(presentid)
#                                model_mgr.set_delete(present)
#                                
#                                # 受け取りフラグを消す.
#                                model = PresentEveryoneReceiveMypage.getByKeyForUpdate(modelid)
#                                model_mgr.set_delete(model)
#                                
#                                def writeEnd():
#                                    BackendApi.remove_present(uid, presentid)
#                                model_mgr.add_write_end_method(writeEnd)
#                                
#                                model_mgr.write_all()
#                                return model_mgr
#                            db_util.run_in_transaction(tr_present, model.id, uid, present.id).write_end()
#                            delete_num += 1
#                        print '%s=>present %d' % (uid, present.id)
#            offset += LIMIT - delete_num
        
        print '================================'
        print 'all done..'
