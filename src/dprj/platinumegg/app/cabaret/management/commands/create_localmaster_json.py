# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import os
from platinumegg.app.cabaret.util.master_data import MasterData

class Command(BaseCommand):
    """ローカルのテスト用に仮のマスターデータをJSON形式で保存する.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'create_localmaster_json'
        print '================================'
        
        jsonstr = MasterData.to_json()
        
        filepath = os.path.join(os.path.dirname(__file__), '../../models/localdata/master.json')
        f = None
        try:
            f = open(filepath, "w")
            f.write(jsonstr)
            print '---------------'
            print 'output file:%s' % filepath
        except Exception, e:
            print '---------------'
            print 'error: %s' % e
        finally:
            if f:
                f.close()
