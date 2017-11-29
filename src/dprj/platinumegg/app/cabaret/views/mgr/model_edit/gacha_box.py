# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Gacha import GachaBoxMaster
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.util.gacha import GachaBoxGroupData
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.models.Gacha import GachaGroupMaster
from platinumegg.app.cabaret.models.NgCast import NgCastMaster
from platinumegg.app.cabaret.util.api import BackendApi
import settings
import settings_sub_props
from enviroment_type import EnvironmentType


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaBoxMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )

    def setting_property(self):
        self.MODEL_LABEL = u'引き抜きのBOX情報'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return
        cnt = 0
        rate_total = 0
        try:
            for data in master.box:
                groupdata = GachaBoxGroupData.createByBoxData(data)
                groupdata.validate(self.getModelMgr())
                if 0 < groupdata.rate:
                    cnt += 1
                    rate_total += groupdata.rate
        except CabaretError, err:
            raise ModelEditValidError('%s, box=%d' % (err.value, master.id))
        if AppRandom.RAND_MAX < rate_total:
            raise ModelEditValidError('rateの上限(65535)を超えています, gacha=%d' % master.id)
        elif cnt == 0:
            raise ModelEditValidError('全ての出現率が0です, gacha=%d' % master.id)

        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'IDが重複しています.id={}'.format(master.id))

    def valid_insert(self, master):
        model_mgr = self.getModelMgr()
        gachagroup_ids = [box['id'] for box in master.box]

        # flag = 0  (False)--> do not insert
        # flag = 1 (True) --> insert
        flag = True

        ng_groups = []
        for group_id in gachagroup_ids:
            group_data = model_mgr.get_model(GachaGroupMaster, group_id, using=settings.DB_READONLY)
            cardid_list = [t['id'] for t in group_data.table]
            ngcast_list = BackendApi.get_model_list(model_mgr, NgCastMaster, cardid_list, using=settings.DB_READONLY)
            if ngcast_list:
                flag = ngcast_list[0].flag
                ng_groups.append(group_id)
        if ng_groups and not flag:
                raise ModelEditValidError(u'NGキャストを含んだグループが含まれています.id={}, ng_groups={}'.format(master.id, ng_groups))

        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)

    def allow_csv(self):
        return True

def main(request):
    return Handler.run(request)
