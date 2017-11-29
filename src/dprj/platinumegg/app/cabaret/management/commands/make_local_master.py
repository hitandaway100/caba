# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import os
from platinumegg.app.cabaret.util.master_data import MasterData
import sys
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class Command(BaseCommand):
    """ローカルのテスト用に仮のマスターデータを作成する.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'make_local_master'
        print '================================'
        
        filepath = os.path.join(os.path.dirname(__file__), '../../models/localdata/master.json')
        print '---------------'
        print 'file: %s' % filepath
        print '---------------'
        
        f = None
        try:
            f = open(filepath, "r")
            jsonstr = f.read()
            modellist = MasterData.update_from_json(jsonstr)
            print 'success:record num=%d' % len(modellist)
        except:
            print 'error: %s' % CabaretError.makeErrorTraceString(sys.exc_info())
        finally:
            if f:
                f.close()
