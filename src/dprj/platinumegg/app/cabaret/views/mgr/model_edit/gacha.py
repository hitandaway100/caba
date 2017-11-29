# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.mgr.model_edit import AdminModelEditHandler,\
    AppModelForm, AppModelChoiceField, ModelEditValidError
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaBoxMaster,\
    GachaStepupMaster, GachaSeatTableMaster, GachaPlayData, GachaGroupMaster
from platinumegg.app.cabaret.models.GachaExplain import GachaExplainMaster
from defines import Defines
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.Present import PrizeMaster
from platinumegg.app.cabaret.util.gacha import GachaBox, GachaMasterSet,\
    GachaBoxGroup
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.TradeShop import TradeShopMaster

class Handler(AdminModelEditHandler):
    """マスターデータの操作.
    """
    class Form(AppModelForm):
        class Meta:
            model = GachaMaster
            exclude = (
                Defines.MASTER_EDITTIME_COLUMN,
                'premium',
            )
        schedule = AppModelChoiceField(ScheduleMaster, required=False, label=u'期間')
        boxid = AppModelChoiceField(GachaBoxMaster, required=False, label=u'BoxID')
        rarity_fixed_boxid = AppModelChoiceField(GachaBoxMaster, required=False, label=u'レアリティ確定の際に使用するBoxID')
        stepid = AppModelChoiceField(GachaStepupMaster, required=False, label=u'StepID')
        stepsid = AppModelChoiceField(GachaMaster, required=False, label=u'ステップ開始ガチャID')
        seattableid = AppModelChoiceField(GachaSeatTableMaster, required=False, label=u'シートテーブルID')
        trade_shop_master_id = AppModelChoiceField(TradeShopMaster, required=False, label=u'TradeShopMasetrID')
        gacha_explain_text_id = AppModelChoiceField(GachaExplainMaster, required=False, label=u'GachaExplainTextID')

    def setting_property(self):
        self.MODEL_LABEL = u'引き抜き(ガチャ)'
        self.valid_error_num = 0

    def __valid_master(self, master):
        model_mgr = self.getModelMgr()

        if not master.is_public:
            return

        boxmaster = GachaBoxMaster.getByKey(master.boxid)
        if boxmaster is None:
            raise ModelEditValidError(u'存在しないBOXが設定されています.gacha=%d' % master.id)

        if master.stepid != 0:
            stepmaster = GachaStepupMaster.getByKey(master.stepid)
            if stepmaster is None:
                raise ModelEditValidError(u'存在しないSTEPが設定されています.gacha=%d' % master.id)

        if master.seattableid:
            seatmaster = GachaSeatTableMaster.getByKey(master.seattableid)
            if seatmaster is None:
                raise ModelEditValidError(u'存在しないシートテーブルが設定されています.gacha=%d' % master.id)

        if master.gacha_explain_text_id:
            gachaexplainmaster = GachaExplainMaster.getByKey(master.gacha_explain_text_id)
            if gachaexplainmaster is None:
                raise ModelEditValidError(u'存在しないGachaExplainMasterが設定されています.gacha=%d' % master.id)

        if self.valid_error_num < 10:
            for record in self.allmasters:
                if master.id == record.id:
                    self.valid_error_num += 1
                    raise ModelEditValidError(u'IDが重複しています.id={}'.format(master.id))

        master.bonus = master.bonus or []
        if master.bonus:
            def checkBonus(bonus):
                items = {}
                for item in PrizeMaster.getByKey(bonus):
                    items[item.id] = item
                for itemid in bonus:
                    if items.get(itemid) is None:
                        raise ModelEditValidError(u'存在しない引抜のおまけアイテムが設定されています.gacha=%d' % master.id)

            if isinstance(master.bonus[0], dict):
                for data in master.bonus:
                    if data.get('rate', 0) < 1:
                        raise ModelEditValidError(u'確率がないおまけが設定されています.gacha=%d' % master.id)
                    elif not data.get('prize'):
                        raise ModelEditValidError(u'内容がないおまけが設定されています.gacha=%d' % master.id)
                    checkBonus(data['prize'])
            else:
                checkBonus(master.bonus)

        playdata = GachaPlayData.makeInstance(0)
        playdata.mid = master.boxid

        if master.consumetype in Defines.GachaConsumeType.BOX_TYPES:
            # ボックスガチャ.
            if not GachaBox(GachaMasterSet(master, boxmaster), playdata).is_boxgacha:
                raise ModelEditValidError(u'%sなのにBOXでないboxidが指定されています.gacha=%d' % (Defines.GachaConsumeType.NAMES[master.consumetype], master.id))

        if not isinstance(master.variableconsumevalue, dict):
            master.variableconsumevalue = {}

        # 回数別のBOXの検証.
        master.special_boxid = master.special_boxid or []
        if master.special_boxid:
            master_special_boxid = dict(master.special_boxid)
            boxmaster_dict = dict([(bm.id, bm) for bm in GachaBoxMaster.getByKey(master_special_boxid.values())])
            if len(list(set(master_special_boxid.values()))) != len(boxmaster_dict.keys()):
                raise ModelEditValidError(u'存在しないboxidがspecial_boxidに設定されています.gacha=%d' % master.id)

            special_box = dict([(cnt, boxmaster_dict[boxid].box) for cnt, boxid in master.special_boxid])
            box = GachaBox(GachaMasterSet(master, boxmaster), playdata, special_box=special_box)
            try:
                box.validate()
            except CabaretError, err:
                raise ModelEditValidError(u'%s.gacha=%d' % (err.value, master.id))

            # 元のグループのカード.
            cardidlist = []
            for group in GachaGroupMaster.getByKey(box.get_group_id_list()):
                # 各グループの出現率.
                groupdata = GachaBoxGroup(group)
                cardidlist.extend([carddata.card for carddata in groupdata.carddata_list])
            cardidlist = list(set(cardidlist))

            # 回数別のグループのBOX.
            for cnt, boxid in master.special_boxid:
                grouplist = GachaGroupMaster.getByKey(box.get_group_id_list(cnt=cnt))
                for group in grouplist:
                    # 各グループの出現率.
                    groupdata = GachaBoxGroup(group)
                    for carddata in groupdata.carddata_list:
                        if not carddata.card in cardidlist:
                            raise ModelEditValidError(u'%d回目のBOXにしか存在しないカードが有ります.gacha=%d,group=%d,card=%d' % (cnt, master.id, group.id, carddata.card))
        self.__valid_rarity_fixed_boxid(model_mgr, master)
        model_mgr.write_all()

    def __valid_rarity_fixed_boxid(self, model_mgr, master):
        if master.consumetype == Defines.GachaConsumeType.FIXEDSR:
            if master.rarity_fixed_boxid == 0:
                raise ModelEditValidError(u'消費するものがSR確定ガチャですが、「レアリティ確定の際に使用するBoxID」が未設定です.gacha=%d' % master.id)
            if master.rarity_fixed_num <= 0:
                raise ModelEditValidError(u'消費するものがSR確定ガチャですが、「レアリティ確定枚数」が0以下です.gacha=%d' % master.id)

            model = model_mgr.get_model(GachaBoxMaster, master.rarity_fixed_boxid)
            if model is None:
                raise ModelEditValidError(u'「レアリティ確定の際に使用するBoxID」に、GachaBoxMasterに存在しないIDが指定されています.gacha=%d' % master.id)

    def valid_insert(self, master):
        self.__valid_master(master)

    def valid_update(self, master):
        self.__valid_master(master)

    def allow_csv(self):
        return True

def main(request):
    return Handler.run(request)
