# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.redisdb import RedisModel
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Card import Card
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class Command(BaseCommand):
    """Redis内のフレンド一覧とカード一覧を消す.
    """
    def handle(self, *args, **options):
        
#        uid_list = (
#            5,
#            142927,
#            142702,
#            142413,
#            142177,
#            141773,
#            141142,
#            140679,
#            140510,
#            139896,
#            139206,
#            138892,
#            138882,
#            138380,
#            137618,
#            137441,
#            137198,
#            136769,
#            136729,
#            136383,
#            136076,
#            135863,
#            135265,
#            135018,
#            133637,
#            133377,
#            133245,
#            133087,
#            132508,
#            131708,
#            131684,
#            131217,
#            129689,
#            129672,
#            128334,
#            127452,
#            126730,
#            126551,
#            126359,
#            125413,
#            124413,
#            124081,
#            123502,
#            123276,
#            123182,
#            123086,
#            122663,
#            121682,
#            121447,
#            120378,
#            120224,
#            119539,
#            118344,
#            115990,
#            114852,
#            114802,
#            114765,
#            113959,
#            113221,
#            112996,
#            111318,
#            109272,
#            109114,
#            108942,
#            108771,
#            108748,
#            108664,
#            108365,
#            108250,
#            108145,
#            106770,
#            106474,
#            105621,
#            103726,
#            103590,
#            103114,
#            101811,
#            101805,
#            101686,
#            101399,
#            101187,
#            100986,
#            100909,
#            100616,
#            100409,
#            99927,
#            99724,
#            98702,
#            97335,
#            96754,
#            96034,
#            95933,
#            94581,
#            94516,
#            91956,
#            91107,
#            90939,
#            90171,
#            89496,
#            89361,
#            89237,
#            89021,
#            86396,
#            84414,
#            82889,
#            82751,
#            80707,
#            76836,
#            76796,
#            76734,
#            76059,
#            72357,
#            71135,
#            69565,
#            67323,
#            66410,
#            66352,
#            66327,
#            65830,
#            65130,
#            63588,
#            62426,
#            62124,
#            61777,
#            58634,
#            57621,
#            56803,
#            56184,
#            55864,
#            54157,
#            51287,
#            47022,
#            45807,
#            45708,
#            45528,
#            44803,
#            43644,
#            42666,
#            41879,
#            41351,
#            41279,
#            41161,
#            40379,
#            39876,
#            39372,
#            38964,
#            37470,
#            35761,
#            35640,
#            35032,
#            32165,
#            31117,
#            29387,
#            28368,
#            28093,
#            26098,
#            24391,
#            23765,
#            20800,
#            20684,
#            17322,
#            16014,
#            14523,
#            12722,
#            8823,
#            7812,
#            7621,
#            7440,
#            7351,
#            7001,
#            6998,
#            6233,
#            4776,
#            2551,
#            2044,
#            1980,
#            1046,
#            806,
#        )
#        redisdb = RedisModel.getDB()
#        for uid in uid_list:
#            cardlist = Card.fetchByOwner(uid)
#            cardidlist = [card.id for card in cardlist]
#            model_mgr = ModelRequestMgr()
#            model_mgr.set_got_models(cardlist)
#            cardsetlist = BackendApi.get_cards(cardidlist)
#            
#            pipe = redisdb.pipeline()
#            for cardset in cardsetlist:
#                BackendApi.save_cardidset(cardset, pipe)
#            pipe.execute()
#            print '%s...OK' % uid
        
        uid_max = Player.max_value('id')
        
#        redisdb = RedisModel.getDB()
        for i in xrange(0, uid_max):
#        for uid in uid_list:
            uid = uid_max - i
            
            cardnum = BackendApi.get_cardnum(uid)
            db_cardnum = Card.count(filters={"uid":uid})
            if db_cardnum == cardnum:
                continue
            print '%s..NG' % uid
        
        print '================================'
        print 'all done'
