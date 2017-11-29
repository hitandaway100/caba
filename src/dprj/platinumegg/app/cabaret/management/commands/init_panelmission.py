# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Mission import PlayerPanelMission,\
    PanelMissionData
from platinumegg.app.cabaret.models.base.queryset import Query

class Command(BaseCommand):
    """パネルミッションを初期化.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'init_panelmission'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        delete_target_model_cls_list = (
            PlayerPanelMission,
            PanelMissionData,
        )
        def tr():
            for model_cls in delete_target_model_cls_list:
                tablename = model_cls.get_tablename()
                query_string = "truncate table `%s`;" % tablename
                Query.execute_update(query_string, [], False)
                print 'delete...%s' % tablename
        db_util.run_in_transaction(tr)
        
        # キャッシュを消す.
        OSAUtil.get_cache_client().flush()
        
        print '================================'
        print 'all done.'
