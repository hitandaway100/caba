# -*- coding: utf-8 -*-

from collections import Counter
from operator import itemgetter

from platinumegg.app.cabaret.kpi.csv.produceevent import ProduceEventCSVBase
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import PlayerEducation
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings


class Manager(ProduceEventCSVBase):
    """プロデュースイベントレベル到達人数分布.
    """
    def __init__(self, date, output_dir):
        ProduceEventCSVBase.__init__(self, date, output_dir)

    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getProduceEventId(model_mgr)

        query = 'SELECT cast_order, level, heart FROM {table} WHERE mid = {mid};'.format(
            table=PlayerEducation.get_tablename(), mid=eventid
        )
        executed = Query.execute_all(query, [], settings.DB_READONLY)
        data = Counter(executed)
        if not data:
            return None

        result = [['cast_order', 'level', 'heart', 'total_player'], ]
        keys = data.keys()
        keys.sort(key=itemgetter(0, 1))
        for key in keys:
            result.append(
                [key[0], key[1], key[2], data[key]]
            )

        return result
