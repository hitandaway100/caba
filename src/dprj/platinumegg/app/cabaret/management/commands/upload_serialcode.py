# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.SerialCampaign import SerialCampaignMaster,\
    SerialCode

class Command(BaseCommand):
    """シリアルコードの登録.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'upload_serialcode'
        print '================================'
        
        # マスターID.
        mid = int(args[0])
        master = SerialCampaignMaster.getByKey(mid)
        if master is None:
            print 'master is not found. id=%s' % mid
            return
        
        # シリアルコードのファイル.
        filepath = args[1]
        fobj = open(filepath)
        
        s = fobj.readline()
        
        codelist = []
        counts = {}
        
        def countUp(code, name):
            counts[name] = counts.get(name, 0) + 1
            print '%s...%s' % (code, name)
        
        def write():
            def tr(codelist, mid):
                model_mgr = ModelRequestMgr()
                for code in codelist:
                    model = SerialCode()
                    model.serial = code
                    model.mid = mid
                    model_mgr.set_save(model)
                model_mgr.write_all()
                return model_mgr
            db_util.run_in_transaction(tr, codelist, mid).write_end()
        
        while 0 < len(s):
            code = s.replace('\n', '').replace('\r', '')
            s = fobj.readline()
            
            if not code:
                continue
            
            model = SerialCode.fetchValues(filters={'serial':code})
            if model:
                if model.mid == mid:
                    countUp(code, 'exists')
                else:
                    countUp(code, 'duplicate')
                continue
            
            codelist.append(code)
            countUp(code, 'append')
            
            if 1000 < len(codelist):
                write()
                codelist = []
        if codelist:
            write()
        
        print '================================'
        print 'all end..'
        print 'update %s' % ','.join(['%s=%s' % (k,v) for k,v in counts.items()])
