# -*- coding: utf-8 -*-

from collections import Counter

from platinumegg.app.cabaret.kpi.csv.produceevent import ProduceEventCSVBase
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventScoutPlayData
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings


class Manager(ProduceEventCSVBase):
    """プロデュースイベントステージ到達人数分布.
    """
    def __init__(self, date, output_dir):
        ProduceEventCSVBase.__init__(self, date, output_dir)

    def get_data(self):
        def tuple_to_int(v):
            """ Since a return value of Query.execute_all() is tuple, set it to int.
            """
            return int(v[0])

        model_mgr = ModelRequestMgr()
        eventid = self.getProduceEventId(model_mgr)

        query = 'SELECT stage FROM {table} WHERE mid = {mid};'.format(
            table=ProduceEventScoutPlayData.get_tablename(), mid=eventid
        )
        executed = Query.execute_all(query, [], using=settings.DB_READONLY)
        data = Counter(executed)
        if not data:
            return None

        result = [['stage', 'total_player'], ]
        stagelist = data.keys()
        stagelist.sort(key=tuple_to_int)
        for stage in stagelist:
            result.append([tuple_to_int(stage), data[stage]])
        return result
