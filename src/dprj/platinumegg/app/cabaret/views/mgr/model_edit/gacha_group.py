# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, ModelEditValidError
from platinumegg.app.cabaret.models.Gacha import GachaGroupMaster
from platinumegg.app.cabaret.models.NgCast import NgCastMaster
from defines import Defines
from platinumegg.app.cabaret.util.gacha import GachaBoxGroup
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
import settings_sub_props
from enviroment_type import EnvironmentType


class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaGroupMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
            )

    def setting_property(self):
        self.MODEL_LABEL = u'引き抜きのカードグループ'
        self.valid_error_num = 0

    def __valid_master(self, master):
        if not master.is_public:
            return
        try:
            group = GachaBoxGroup(master)
            group.validate(self.getModelMgr())
        except CabaretError, err:
            raise ModelEditValidError('%s, gachagroup=%d' % (err.value, master.id))

        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'IDが重複しています.id={}'.format(master.id))

    def valid_insert(self, master):
        # check if the the GroupMaster object contains casts from NgCastMaster
        model_mgr = self.getModelMgr()
        castid_list = [table["id"] for table in master.table] # master.table is a list of dictionaries
        ngcast_list = BackendApi.get_model_list(model_mgr, NgCastMaster, castid_list, using=settings.DB_READONLY)

        if ngcast_list:
            # flag = 0  (False)--> do not insert
            # flag = 1 (True) --> insert
            flag = ngcast_list[0].flag
            # raise error
            if not flag:
                error_msg = u"ガチャグループマスターはNGキャストが含まれています。group_master_id={} ".format(master.id)
                for ngcast in ngcast_list:
                    error_msg += u"[cast_id={}, cast_name={}] ".format(ngcast.id, ngcast.name)

                k = error_msg.rfind("<br/>")
                error_msg = error_msg[:k]
                raise ModelEditValidError(error_msg)

        # if everything is ok, continue validation by calling __valid_master
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)

    def allow_csv(self):
        return True


def main(request):
    return Handler.run(request)
