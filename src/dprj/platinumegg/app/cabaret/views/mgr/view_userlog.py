# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from defines import Defines
from platinumegg.app.cabaret.models.UserLog import UserLogLoginBonus,\
    UserLogCardGet, UserLogCardSell, UserLogComposition, UserLogEvolution,\
    UserLogGacha, UserLogAreaComplete, UserLogScoutComplete,\
    UserLogPresentReceive, UserLogItemGet, UserLogItemUse,\
    UserLogTreasureGet, UserLogTreasureOpen, UserLogTrade, UserLogPresentSend,\
    UserLogTicketGet, UserLogLoginBonusTimeLimited, UserLogComeBack,\
    UserLogCardStock, UserLogBattleEventPresent, UserLogScoutEventGachaPt,\
    UserLogRankingGachaWholePrize, UserLogScoutEventTipGet, UserLogLevelUpBonus,\
    UserLogLoginbonusSugoroku, UserLogCabaClubStore, UserLogTradeShop, UserLogReprintTicketTradeShop
import settings
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Scout import ScoutMaster
from platinumegg.app.cabaret.util.present import PresentSet
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventStageMaster
from platinumegg.app.cabaret.models.AccessBonus import LoginBonusSugorokuMapSquaresMaster

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """ユーザーログ確認.
    """
    def process(self):
        self.html_param['_logtype'] = None
        
        uid = self.__get_uid()
        if not uid:
            args = self.getUrlArgs('/infomations/view_userlog/')
            uid = str(args.get(0))
            if uid.isdigit():
                uid = int(uid)
                self.html_param['_serchtype'] = 'uid'
                self.html_param['_value'] = uid
            else:
                uid = None
        if uid:
            self.__putUserLog(int(uid))
            self.html_param['_uid'] = uid
        
        
        self.html_param['Defines'] = Defines
        self.html_param['url_view_userlog'] = self.makeAppLinkUrlAdmin(UrlMaker.mgr_infomations('view_userlog'))
        self.writeAppHtml('infomations/view_userlog')
    
    TABLE = {
        Defines.UserLogType.LOGINBONUS:UserLogLoginBonus,
        Defines.UserLogType.LOGINBONUS_TIMELIMITED:UserLogLoginBonusTimeLimited,
        Defines.UserLogType.CARD_GET:UserLogCardGet,
        Defines.UserLogType.CARD_SELL:UserLogCardSell,
        Defines.UserLogType.COMPOSITION:UserLogComposition,
        Defines.UserLogType.EVOLUTION:UserLogEvolution,
        Defines.UserLogType.GACHA:UserLogGacha,
        Defines.UserLogType.AREA_COMPLETE:UserLogAreaComplete,
        Defines.UserLogType.SCOUT_COMPLETE:UserLogScoutComplete,
        Defines.UserLogType.PRESENT_RECEIVE:UserLogPresentReceive,
        Defines.UserLogType.PRESENT_SEND:UserLogPresentSend,
        Defines.UserLogType.ITEM_GET:UserLogItemGet,
        Defines.UserLogType.ITEM_USE:UserLogItemUse,
        Defines.UserLogType.TREASURE_GET:UserLogTreasureGet,
        Defines.UserLogType.TREASURE_OPEN:UserLogTreasureOpen,
        Defines.UserLogType.TRADE:UserLogTrade,
        Defines.UserLogType.ADDITIONAL_TICKET:UserLogTicketGet,
        Defines.UserLogType.COMEBACK:UserLogComeBack,
        Defines.UserLogType.CARDSTOCK:UserLogCardStock,
        Defines.UserLogType.BATTLEEVENT_PRESENT:UserLogBattleEventPresent,
        Defines.UserLogType.SCOUTEVENT_GACHAPT:UserLogScoutEventGachaPt,
        Defines.UserLogType.RANKINGGACHA_WHOLEPRIZE:UserLogRankingGachaWholePrize,
        Defines.UserLogType.SCOUTEVENT_TIPGET:UserLogScoutEventTipGet,
        Defines.UserLogType.LOGINBONUS_SUGOROKU:UserLogLoginbonusSugoroku,
        Defines.UserLogType.LEVELUP_BONUS:UserLogLevelUpBonus,
        Defines.UserLogType.CABACLUB_STORE:UserLogCabaClubStore,
        Defines.UserLogType.POINTCHANGE_TRADESHOP:UserLogTradeShop,
        Defines.UserLogType.TICKET_TRADESHOP:UserLogReprintTicketTradeShop,
    }
    
    def __get_uid(self):
        serchtype = self.request.get('_serchtype')
        v = self.request.get('_value')
        
        self.html_param['_serchtype'] = serchtype
        self.html_param['_value'] = v
        
        uid = None
        if serchtype == 'uid':
            uid = str(v)
            if uid and uid.isdigit():
                uid = int(uid)
            else:
                uid = None
        elif serchtype == 'dmmid':
            dmmid = str(v)
            uid = BackendApi.dmmid_to_appuid(self, [dmmid], using=backup_db).get(dmmid)
        return uid
    
    def __putUserLog(self, uid):
        """ユーザーログを埋め込む.
        """
        page = 0
        logtype = str(self.request.get('_logtype'))
        if not logtype.isdigit() or not Handler.TABLE.has_key(int(logtype)):
            args = self.getUrlArgs('/infomations/view_userlog/')
            logtype = str(args.get(1))
            if not logtype.isdigit() or not Handler.TABLE.has_key(int(logtype)):
                return
            page = str(args.get(2))
            if page.isdigit():
                page = int(page)
            else:
                return
        logtype = int(logtype)
        
        self.html_param['titles'] = self.__get_titles(logtype)
        
        model_list, has_next_page = self.__getModel(logtype, uid, page)
        objlist = [self.__model_to_htmlobj(model) for model in model_list]
        self.execute_api()
        self.html_param['userlog_list'] = objlist
        
        if not objlist:
            self.putAlertToHtmlParam(u'ログが見つかりませんでした', AlertCode.WARNING)
        
        self.html_param['_logtype'] = logtype
        
        if 0 < page:
            url = UrlMaker.mgr_infomations( 'view_userlog', uid, logtype, page - 1 )
            self.html_param['url_prev'] = self.makeAppLinkUrl(url)
        if has_next_page:
            url = UrlMaker.mgr_infomations( 'view_userlog', uid, logtype, page + 1 )
            self.html_param['url_next'] = self.makeAppLinkUrl(url)
    
    def __get_titles(self, logtype):
        FUNCTION_FORMAT = '_get_title_{modelname}'
        funcname = FUNCTION_FORMAT.format(modelname=Handler.TABLE.get(logtype).__name__)
        
        titles = ['日付']
        f = getattr(self, funcname, None)
        if f:
            data_titles = f()
            if data_titles:
                titles.extend(data_titles)
        return titles
    
    def __getModel(self, logtype, uid, page = 0):
        """モデルを取得.
        """
        page_count = 200
        offset = page * page_count
        limit = page_count + 1
    
        model_cls = Handler.TABLE[logtype]
        model_list = model_cls.fetchValues(filters={'uid':uid}, order_by='-ctime', offset = offset, limit=limit, using=backup_db)
        has_next_page = len(model_list) == limit
        model_list = model_list[:page_count]
        return model_list, has_next_page
    
    def __model_to_htmlobj(self, model):
        """テキストに変換.
        """
        FUNCTION_FORMAT = '_get_data_{modelname}'
        funcname = FUNCTION_FORMAT.format(modelname=model.get_class_name())
        return {
            'ctime' : model.ctime.strftime(u'%Y/%m/%d %H:%M:%S'),
            'data' : getattr(self, funcname)(model),
        }
    #====================================================
    # ログインボーナス.
    def _get_title_UserLogLoginBonus(self):
        return [u'連続ログイン', u'通算ログイン', u'累計ログインボーナス日数', u'累計ログイン']
    
    def _get_data_UserLogLoginBonus(self, model):
        return model.ldays, model.pdays, model.data.get('tldays') or 0, model.data.get('tldays_view') or 0
    
    #====================================================
    # ロングログインボーナス.
    def _get_title_UserLogLoginBonusTimeLimited(self):
        return [u'マスター', u'ログイン日数']
    
    def _get_data_UserLogLoginBonusTimeLimited(self, model):
        model_mgr = self.getModelMgr()
        mid = model.mid
        master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, mid, using=backup_db)
        name = self._mastername(master)
        return u'%s(ID:%s)' % (name, mid), model.days
    
    #====================================================
    # カード獲得.
    def _get_title_UserLogCardGet(self):
        return [u'カード', u'獲得方法', u'自動退店']
    
    def _get_data_UserLogCardGet(self, model):
        model_mgr = self.getModelMgr()
        mid = model.mid
        way = model.way
        autosell = bool(model.autosell)
        cardmaster = model_mgr.get_model(CardMaster, mid, using=backup_db)
        cardname = self._mastername(cardmaster)
        return u'{cardname}(MID:{mid})'.format(cardname=cardname, mid=mid), way, autosell
    
    #====================================================
    # カード売却.
    def _get_title_UserLogCardSell(self):
        return [u'売却したカード', u'価格', u'キャバ王の秘宝']
    
    def _get_data_UserLogCardSell(self, model):
        CARDTEXT_FORMAT = u'{name}(ID:{cardid},Lv:{level},CG:{price},CG:{treasure})'
        
        model_mgr = self.getModelMgr()
        cardidlist = model.cardidlist
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=backup_db, deleted=True)
        sellprice = model.price
        treasure = model.treasure
        
        cardnames = []
        for cardset in cardlist:
            cardnames.append(CARDTEXT_FORMAT.format(name=cardset.master.name, cardid=cardset.id, level=cardset.card.level, price=cardset.sellprice, treasure=cardset.sellprice_treasure))
        
        return cardnames, sellprice, treasure
    
    #====================================================
    # 教育.
    def _get_title_UserLogComposition(self):
        return [u'ベース', u'素材', u'経験値', u'大成功', u'教育後サービスレベル', u'サービスレベル上昇']
    
    def _get_data_UserLogComposition(self, model):
        model_mgr = self.getModelMgr()
        
        def makeCardText(model_cardobj):
            master = model_mgr.get_model(CardMaster, model_cardobj['mid'], using=backup_db)
            name = self._mastername(master)
            return u'{name}(ID:{cardid},MID:{mid},exp:{exp})'.format(name=name, cardid=model_cardobj['id'], mid=model_cardobj['mid'], exp=model_cardobj['exp'])
        
        basecard = makeCardText(model.basecard)
        materiallist = [makeCardText(material) for material in model.materiallist]
        return basecard, materiallist, model.exp, model.is_great, model.data.get('slv', u'--'), model.data.get('slvup', u'--')
    
    #====================================================
    # 教育.
    def _get_title_UserLogEvolution(self):
        return [u'ベース', u'素材', u'接客力引継']
    
    def _get_data_UserLogEvolution(self, model):
        model_mgr = self.getModelMgr()
        
        def makeCardText(model_cardobj):
            master = model_mgr.get_model(CardMaster, model_cardobj['mid'], using=backup_db)
            name = self._mastername(master)
            return u'{name}(ID:{cardid},level:{level},power:{power})'.format(name=name, cardid=model_cardobj['id'], level=model_cardobj['level'], power=model_cardobj['power'])
        
        return makeCardText(model.basecard), makeCardText(model.material), model.takeover
    
    #====================================================
    # ガチャ.
    def _get_title_UserLogGacha(self):
        arr = [u'ガチャ名', u'タイプ', u'価格']
        arr.extend([u'結果[%s]' % Defines.Rarity.NAMES[rare] for rare in Defines.Rarity.LIST])
        arr.extend([u'初回', u'獲得ポイント', u'累計ポイント', u'総計ポイント'])
        return arr
    
    def _get_data_UserLogGacha(self, model):
        NAME_FORMAT = u'{name}(MID:{mid})'
        
        model_mgr = self.getModelMgr()
        mid = model.mid
        consumevalue = model.consumevalue
        is_first = model.is_first
        cardidlist = model.cardidlist
        gachamaster = BackendApi.get_gachamaster(model_mgr, mid, using=backup_db)
        cardmasters = BackendApi.get_cardmasters(cardidlist, model_mgr, using=backup_db)
        
        name = NAME_FORMAT.format(mid=mid, name=self._mastername(gachamaster))
        
        cardnames = {}
        for cardid in cardidlist:
            master = cardmasters.get(cardid)
            rare = Defines.Rarity.NORMAL
            if master:
                rare = master.rare
            arr = cardnames[rare] = cardnames.get(rare) or []
            arr.append(NAME_FORMAT.format(mid=cardid, name=self._mastername(master)))
        
        consumetype = u'不明'
        if gachamaster:
            consumetype = Defines.GachaConsumeType.NAMES.get(gachamaster.consumetype, consumetype)
        data = [
            name, consumetype, consumevalue
        ]
        data.extend([cardnames.get(rare) or [] for rare in Defines.Rarity.LIST])
        data.extend([is_first, model.point_add, model.point_total, model.point_whole])
        
        return data
    
    #====================================================
    # エリア達成.
    def _get_title_UserLogAreaComplete(self):
        return [u'エリア']
    
    def _get_data_UserLogAreaComplete(self, model):
        model_mgr = self.getModelMgr()
        area = model.area
        is_event = model.data.get('is_event', False)
        if is_event:
            stagemaster = BackendApi.get_model(model_mgr, ScoutEventStageMaster, area, using=backup_db)
            if stagemaster:
                name = stagemaster.areaname
            else:
                name = u'不明'
            return [u'[イベ]{name}(ID:{scout})'.format(scout=area, name=name)]
        else:
            areamaster = BackendApi.get_area(model_mgr, area, using=backup_db)
            return [u'{name}(ID:{area})'.format(area=area, name=self._mastername(areamaster))]
    
    #====================================================
    # スカウト達成.
    def _get_title_UserLogScoutComplete(self):
        return [u'スカウト']
    
    def _get_data_UserLogScoutComplete(self, model):
        model_mgr = self.getModelMgr()
        scout = model.scout
        is_event = model.data.get('is_event', False)
        if is_event:
            stagemaster = BackendApi.get_model(model_mgr, ScoutEventStageMaster, scout, using=backup_db)
            return [u'[イベ]{name}(ID:{scout})'.format(scout=scout, name=self._mastername(stagemaster))]
        else:
            scoutmaster = BackendApi.get_model(model_mgr, ScoutMaster, scout, using=backup_db)
            return [u'{name}(ID:{scout})'.format(scout=scout, name=self._mastername(scoutmaster))]
    
    #====================================================
    # プレゼント受取.
    def _get_title_UserLogPresentReceive(self):
        return [u'内容', '文言']
    
    def _get_data_UserLogPresentReceive(self, model):
        model_mgr = self.getModelMgr()
        presentid = model.presentid
        
        presentsetlist = PresentSet.collect(model_mgr, [presentid], using=backup_db, received=True)
        if presentsetlist:
            presentset = presentsetlist[0]
            content = u'{name}{numtext}'.format(name=presentset.itemname, numtext=presentset.numtext_with_x)
            text = presentset.text
        else:
            content = u'不明(ID:{presentid})'.format(presentid=presentid)
            text = u'--------'
        return content, text
    
    #====================================================
    # プレゼント送信.
    def _get_title_UserLogPresentSend(self):
        return [u'内容', '文言', '受取済', '期限切れ']
    
    def _get_data_UserLogPresentSend(self, model):
        model_mgr = self.getModelMgr()
        presentid = model.presentid
        
        received = False
        timeover = False
        
        presentsetlist = PresentSet.collect(model_mgr, [presentid], using=backup_db, received=True)
        if presentsetlist:
            received = True
        else:
            presentsetlist = PresentSet.collect(model_mgr, [presentid], using=backup_db, received=False)
            if not presentsetlist:
                timeover = True
        
        presentset = PresentSet.presentToPresentSet(model_mgr, [model], using=backup_db)[0]
        content = u'{name}{numtext}'.format(name=presentset.itemname, numtext=presentset.numtext_with_x)
        text = presentset.text
        
        return content, text, received, timeover
    
    #====================================================
    # アイテム獲得.
    def _get_title_UserLogItemGet(self):
        return [u'アイテム名', u'獲得数', u'加算後の所持数', u'獲得数(無料)', u'獲得数(課金)', u'加算後の所持数(無料)', u'加算後の所持数(課金)']
    
    def _get_data_UserLogItemGet(self, model):
        model_mgr = self.getModelMgr()
        mid = model.mid
        itemmaster = BackendApi.get_itemmaster(model_mgr, mid, using=backup_db)
        nametext = u'{name}(ID:{iid})'.format(name=self._mastername(itemmaster), iid=mid)
        return nametext, model.vnum_add+model.rnum_add, model.vnum+model.rnum, model.vnum_add, model.rnum_add, model.vnum, model.rnum
    
    #====================================================
    # アイテム使用.
    def _get_title_UserLogItemUse(self):
        return [u'アイテム名', u'使用数', u'減算加算後の所持数', u'使用数(無料)', u'使用数(課金)', u'減算後の所持数(無料)', u'減算後の所持数(課金)']
    
    def _get_data_UserLogItemUse(self, model):
        model_mgr = self.getModelMgr()
        mid = model.mid
        itemmaster = BackendApi.get_itemmaster(model_mgr, mid, using=backup_db)
        nametext = u'{name}(ID:{iid})'.format(name=self._mastername(itemmaster), iid=mid)
        return nametext, model.vnum_rem+model.rnum_rem, model.vnum+model.rnum, model.vnum_rem, model.rnum_rem, model.vnum, model.rnum
    
    #====================================================
    # 宝箱獲得.
    def _get_title_UserLogTreasureGet(self):
        return [u'宝箱種別', u'内容', u'受取済', u'期限切れ']
    
    def _get_data_UserLogTreasureGet(self, model):
        model_mgr = self.getModelMgr()
        treasuretype = model.treasuretype
        mid = model.mid
        treasure = BackendApi.get_treasure(model_mgr, treasuretype, mid, using=backup_db, forupdate=False, deleted=False)
        if treasure:
            opened = False
            master = treasure.master
            if treasure:
                timeover = False
            else:
                timeover = True
        else:
            opened = True
            timeover = False
            treasure = BackendApi.get_treasure(model_mgr, treasuretype, mid, using=backup_db, deleted=True)
            master = treasure.master if treasure else None
        if master:
            info = BackendApi.make_treasureiteminfo_list(self, [master])[0]
            numtext = u'%s%s' % (info['item']['name'], info['item']['numtext'])
        else:
            numtext = u'不明:%d' % mid
        return Defines.TreasureType.NAMES.get(treasuretype, u'不明'), numtext, opened, timeover
    
    #====================================================
    # 宝箱開封.
    def _get_title_UserLogTreasureOpen(self):
        return [u'宝箱種別', u'内容', u'開封後の鍵の数']
    
    def _get_data_UserLogTreasureOpen(self, model):
        model_mgr = self.getModelMgr()
        treasuretype = model.treasuretype
        mid = model.mid
        key_num = model.data.get('post_keynum', 0)
        master = BackendApi.get_treasuremaster(model_mgr, treasuretype, mid, using=backup_db)
        info = BackendApi.make_treasureiteminfo_list(self, [master])[0]
        return Defines.TreasureType.NAMES.get(treasuretype, u'不明'), u'%s%s' % (info['item']['name'], info['item']['numtext']), key_num
    
    #====================================================
    # 秘宝交換.
    def _get_title_UserLogTrade(self):
        return [u'内容', u'交換後のキャバ王の秘宝', u'交換後の裏社会の秘宝']
    
    def _get_data_UserLogTrade(self, model):
        model_mgr = self.getModelMgr()
        mid = model.mid
        master = BackendApi.get_trademaster(model_mgr, mid, using=backup_db)
        
        if master:
            presentlist = BackendApi.create_present(model_mgr, 0, 0, master.itype, master.itemid, master.itemnum, do_set_save=False)
            presentset = PresentSet.presentToPresentSet(model_mgr, presentlist, using=backup_db)[0]
            text = u'%s%s' % (presentset.itemname, presentset.numtext_with_x)
        else:
            text = u'不明'
        return text, model.cabaretking, model.demiworld
    
    #====================================================
    # ガチャチケット.
    def _get_title_UserLogTicketGet(self):
        return [u'種別', u'増減', u'増減後所持数']
    
    def _get_data_UserLogTicketGet(self, model):
        tickettype = model.tickettype
        addnum = model.addnum
        num = model.num
        name = Defines.GachaConsumeType.GachaTicketType.NAMES.get(tickettype, u'不明')
        return name, addnum, num
    
    #====================================================
    # カムバックキャンペーン.
    def _get_title_UserLogComeBack(self):
        return [u'マスター', u'ログイン日数']
    
    def _get_data_UserLogComeBack(self, model):
        model_mgr = self.getModelMgr()
        mid = model.mid
        master = BackendApi.get_comebackcampaignmaster(model_mgr, mid, using=backup_db)
        name = self._mastername(master)
        return u'%s(ID:%s)' % (name, mid), model.days
    
    #====================================================
    # カードのストック.
    def _get_title_UserLogCardStock(self):
        return [u'異動したキャスト', u'内訳', u'異動後のストック数']
    
    def _get_data_UserLogCardStock(self, model):
        model_mgr = self.getModelMgr()
        cardidlist = model.cardidlist
        result_nums = model.result_nums
        cardsetlist = BackendApi.get_cards(cardidlist, model_mgr, using=backup_db, deleted=True)
        cardnamelist = []
        names = {}
        nums = {}
        
        for cardset in cardsetlist:
            
            album = cardset.master.album
            if cardset.master.hklevel == 1:
                master = cardset.master
            else:
                mid = BackendApi.get_cardmasterid_by_albumhklevel(model_mgr, album, 1, using=backup_db)
                master = BackendApi.get_cardmasters([mid], model_mgr, using=backup_db).get(mid)
            
            names[album] = self._mastername(master)
            
            nums[album] = nums.get(album, 0) + 1
            
            cardnamelist.append(u'%s(ID:%s,MID:%s)' % (self._mastername(cardset.master), cardset.id, cardset.master.id))
        
        stocklist = []
        for mid,num in nums.items():
            stocklist.append(u'%s(AlbumID:%s)x%d' % (names[mid], mid, num))
        
        result_num_list = []
        for k,v in result_nums.items():
            result_num_list.append(u'%s(AlbumID:%s)x%d' % (names[k], k, v))
        
        return cardnamelist, stocklist, result_num_list
    
    #====================================================
    # バトルイベント贈り物.
    def _get_title_UserLogBattleEventPresent(self):
        return [u'通し番号', u'中身']
    
    def _get_data_UserLogBattleEventPresent(self, model):
        model_mgr = self.getModelMgr()
        
        # 贈り物.
        master = BackendApi.get_battleeventpresent_master(model_mgr, model.eventid, model.number, using=backup_db)
        name = self._mastername(master)
        
        # 中身.
        contentmaster = BackendApi.get_battleeventpresent_content_master(model_mgr, model.content, using=backup_db)
        content_name = self._mastername(contentmaster)
        
        return u'%s(Number:%s)' % (name, model.number), u'%s(MID:%s)' % (content_name, model.content)
    
    #====================================================
    # カカオ.
    def _get_title_UserLogScoutEventGachaPt(self):
        return [u'イベント', u'変動後', u'変動前', u'増減']
    
    def _get_data_UserLogScoutEventGachaPt(self, model):
        model_mgr = self.getModelMgr()
        
        # イベントマスター.
        master = BackendApi.get_scouteventmaster(model_mgr, model.eventid, using=backup_db)
        name = self._mastername(master)
        
        return u'%s(ID:%s)' % (name, model.eventid), model.pt_post, model.pt_pre, model.pt_add
    
    #====================================================
    # ランキングガチャ報酬.
    def _get_title_UserLogRankingGachaWholePrize(self):
        return [u'ランキング', u'報酬', u'総計Pt']
    
    def _get_data_UserLogRankingGachaWholePrize(self, model):
        model_mgr = self.getModelMgr()
        
        # ランキングマスター.
        master = BackendApi.get_rankinggacha_master(model_mgr, model.boxid, using=backup_db)
        name = self._mastername(master)
        
        # 報酬.
        prizelist = BackendApi.get_prizelist(model_mgr, model.prizes, using=backup_db)
        prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=backup_db)
        prizetextlist = [item['text'] for item in prizeinfo['listitem_list']]
        
        return u'%s(ID:%s)' % (name, model.boxid), prizetextlist, model.wholepoint
    
    #====================================================
    # スカウトイベントチップ獲得.
    def _get_title_UserLogScoutEventTipGet(self):
        return [u'イベント', u'短冊名', u'消費した短冊数', u'消費後の短冊数', u'獲得したチップ数', u'獲得後のチップ数']
    
    def _get_data_UserLogScoutEventTipGet(self, model):
        model_mgr = self.getModelMgr()
        
        # イベント.
        eventmaster = BackendApi.get_scouteventmaster(model_mgr, model.eventid, using=backup_db)
        
        # 短冊.
        tanzakumaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, model.eventid, model.tanzaku_number, using=backup_db)
        
        return u'{}:{}'.format(model.eventid, self._mastername(eventmaster)), u'{}:{}'.format(model.tanzaku_number, self._mastername(tanzakumaster, 'tanzakuname')), model.tanzaku_num, model.tanzaku_num_post, model.tip_num, model.tip_num_post
    
    #====================================================
    # 双六ログインボーナス.
    def _get_title_UserLogLoginbonusSugoroku(self):
        return [u'出目', u'移動ルート']
    
    def _get_data_UserLogLoginbonusSugoroku(self, model):
        model_mgr = self.getModelMgr()
        squares_id_list = model.squares_id_list
        squares_dict = BackendApi.get_model_dict(model_mgr, LoginBonusSugorokuMapSquaresMaster, squares_id_list, using=backup_db)
        arr = []
        for squares_id in squares_id_list:
            master = squares_dict.get(squares_id)
            name = self._mastername(master, attr='name_mgr')
            mapid = master.mid if master else u'---'
            number = master.number if master else u'---'
            arr.append(u'{}(map:{},number:{})'.format(name, mapid, number))
        return model.number, arr
    
    #====================================================
    # レベルアップボーナス.
    def _get_title_UserLogLevelUpBonus(self):
        return [u'到達レベル', u'Version']
    def _get_data_UserLogLevelUpBonus(self, model):
        return model.level, model.mid
    
    #====================================================
    # キャバクラ経営.
    def _get_title_UserLogCabaClubStore(self):
        return [u'店舗', u'種別', u'集客数', u'売上', u'その他']
    def _get_data_UserLogCabaClubStore(self, model):
        # 店舗.
        model_mgr = self.getModelMgr()
        storemaster = BackendApi.get_cabaretclub_store_master(model_mgr, model.storemaster_id, using=backup_db)
        storename = u'{}:{}'.format(model.storemaster_id, self._mastername(storemaster))
        # 種別毎の処理.
        customer, proceeds = [u'------'] * 2
        texts = []
        
        logtype = model.logtype
        if logtype == UserLogCabaClubStore.LogType.OPEN and model.data.has_key('customer'):
            logtype = UserLogCabaClubStore.LogType.ADVANCE
        if logtype == UserLogCabaClubStore.LogType.RENTAL:
            logtype_text = u'レンタル開始'
            texts.append(u'{}日間'.format(model.days))
        elif logtype == UserLogCabaClubStore.LogType.CANCEL:
            logtype_text = u'レンタル終了'
        elif logtype == UserLogCabaClubStore.LogType.OPEN:
            logtype_text = u'開店'
            # スカウトマン.
            texts.append(u'スカウトマン:{}'.format(model.scoutman))
            # 開店時のキャスト.
            texts.append(u'キャスト:{}人'.format(len(model.cardmidlist)))
            cardmaster_dict = BackendApi.get_cardmasters(list(set(model.cardmidlist)), model_mgr, using=backup_db)
            cardinfos = [u'{}(ID:{})x{}'.format(self._mastername(cardmaster), cardid, model.cardmidlist.count(cardid)) for cardid, cardmaster in cardmaster_dict.items()]
            texts.extend(cardinfos)
        elif logtype == UserLogCabaClubStore.LogType.CLOSE:
            logtype_text = u'閉店'
        elif logtype == UserLogCabaClubStore.LogType.ADVANCE:
            logtype_text = u'店舗更新'
            customer, proceeds = model.customer, model.proceeds
            # 発生中のイベント.
            if model.event_id:
                eventmaster = BackendApi.get_cabaretclub_event_master(model_mgr, model.event_id, using=backup_db)
                texts.append(u'発生中のイベント:{}(ID:{})'.format(self._mastername(eventmaster), model.event_id))
            else:
                texts.append(u'発生中のイベント:無し')
            # 発生したイベント.
            if model.event_counts:
                eventmaster_dict = BackendApi.get_cabaretclub_event_master_dict(model_mgr, model.event_counts.keys(), using=backup_db)
                texts.append(u'終了したイベント:')
                texts.extend([u'{}(ID:{})x{}'.format(self._mastername(eventmaster_dict.get(eid)), eid, cnt) for eid, cnt in model.event_counts.items()])
        elif logtype == UserLogCabaClubStore.LogType.USER_ACTION:
            logtype_text = u'対策'
            eventmaster = BackendApi.get_cabaretclub_event_master(model_mgr, model.event_id, using=backup_db)
            texts.append(u'対策したイベント:{}(ID:{})'.format(self._mastername(eventmaster), model.event_id))
        return storename, logtype_text, customer, proceeds, texts
    
    #====================================================
    # チケット交換所.
    def _get_title_UserLogReprintTicketTradeShop(self):
        return [u'トレードID', u'キャストID', u'チケットID', u'個数', u'消費チケット数', u'消費前チケット数']
    def _get_data_UserLogReprintTicketTradeShop(self, model):
        return model.tradeid, model.castid, model.ticketid, model.num, model.use_ticketnum, model.pre_ticketnum

    #====================================================
    # PtChange交換所.
    def _get_title_UserLogTradeShop(self):
        return [u'ショップID', u'ショップアイテムID', u'残りポイント']
    def _get_data_UserLogTradeShop(self, model):
        return model.shopid, model.shopitemid, model.point

    #====================================================
    def _mastername(self, master, attr='name'):
        if master:
            return getattr(master, attr)
        else:
            return u'不明'
    

def main(request):
    return Handler.run(request)
