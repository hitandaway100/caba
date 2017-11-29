# -*- coding: utf-8 -*-
import urllib

class UrlMaker:
    """Url
    """
    @staticmethod
    def simple_html(target):
        return '/simple/%s/' % target

    @staticmethod
    def effect(ope):
        return '/effect/%s' % ope

    @staticmethod
    def invite():
        return '/invite/'

    @staticmethod
    def top():
        return '/'

    @staticmethod
    def warnpage():
        return '/warnpage/'

    @staticmethod
    def mypage():
        return '/mypage'

    @staticmethod
    def myframe():
        return '/myframe'

    @staticmethod
    def regist():
        return '/regist/op'

    @staticmethod
    def regist_select():
        return '/regist/select'

    @staticmethod
    def regist_yesno(ptype, first=True):
        if first:
            return '/regist/yesno/%d/1' % ptype
        else:
            return '/regist/yesno/%d' % ptype

    @staticmethod
    def regist_write(ptype):
        return '/regist/write/%d' % ptype

    @staticmethod
    def regist_decide():
        return '/regist/decide'

    @staticmethod
    def tutorial(skip=False):
        skip = int(bool(skip)) or ''
        return '/tutorial/%s' % skip

    @staticmethod
    def levelupbonus():
        return '/levelupbonus'

    @staticmethod
    def happening():
        return '/happening'

    @staticmethod
    def happeningdo(key):
        return '/happeningdo/%s' % urllib.quote(key, '')

    @staticmethod
    def happeninganim(key):
        return '/happeninganim/%s' % urllib.quote(key, '')

    @staticmethod
    def happeningresultanim(key, idx=0):
        return '/happeningresultanim/%s/%d' % (urllib.quote(key, ''), idx)

    @staticmethod
    def happeningresult(key):
        return '/happeningresult/%s' % urllib.quote(key, '')

    @staticmethod
    def raidfriendselect(raidid):
        return '/raidfriendselect/list/%d/' % raidid

    @staticmethod
    def raidfriendset(raidid, uid):
        return '/raidfriendselect/set/%d/%d/' % (raidid, uid)

    @staticmethod
    def raiddo(raidid, key):
        return '/raid/do/%s/%s/' % (raidid, urllib.quote(key, ''))

    @staticmethod
    def raidanim():
        return '/raid/anim/'

    @staticmethod
    def raidresult():
        return '/raid/result/'

    @staticmethod
    def raidhelpsend():
        return '/raidhelpsend/'

    @staticmethod
    def raidhelpdetail(raidid):
        return '/raidhelpdetail/%s/' % raidid

    @staticmethod
    def raidend(raidid):
        return '/raid/end/%s/' % raidid

    @staticmethod
    def raidresultanim(raidid=''):
        if raidid:
            return '/raid/resultanim/%d/' % raidid
        else:
            return '/raid/resultanim/'

    @staticmethod
    def raidloglist():
        return '/raidlog/'

    @staticmethod
    def raidlogdetail(raidlogid):
        return '/raidlog/%s/' % raidlogid

    @staticmethod
    def happeningend(happeningid):
        return '/happeningend/%s/' % happeningid

    @staticmethod
    def happeningcancel_yesno():
        return '/happeningcancel/yesno'

    @staticmethod
    def happeningcancel_do():
        return '/happeningcancel/do'

    @staticmethod
    def areamap():
        return '/areamap/'

    @staticmethod
    def scout():
        return '/scout/'

    @staticmethod
    def scoutdo(scoutid, key):
        return '/scoutdo/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scoutanim(scoutid, key):
        return '/scoutanim/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scoutresultanim(scoutid, key, idx):
        return '/scoutresultanim/%d/%s/%d' % (scoutid, urllib.quote(key, ''), idx)

    @staticmethod
    def scoutresult(scoutid, key):
        return '/scoutresult/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scoutcardget(scoutid):
        return '/scoutcardget/%d/' % scoutid

    @staticmethod
    def scoutcardgetresult(scoutid):
        return '/scoutcardgetresult/%d/' % scoutid

    @staticmethod
    def bosspre(areaid):
        return '/bosspre/%d' % areaid

    @staticmethod
    def bossbattle(areaid, key):
        return '/bossbattle/%d/%s' % (areaid, urllib.quote(key, ''))

    @staticmethod
    def bossbattleanim(areaid, key):
        return '/bossbattleanim/%d/%s' % (areaid, urllib.quote(key, ''))

    @staticmethod
    def bossresult(areaid, key):
        return '/bossresult/%d/%s' % (areaid, urllib.quote(key, ''))

    @staticmethod
    def bossscenarioanim(areaid, key):
        return '/bossscenarioanim/%d/%s' % (areaid, urllib.quote(key, ''))

    @staticmethod
    def battle():
        return '/battle/'

    @staticmethod
    def battlelp():
        return '/battlelp/'

    @staticmethod
    def battlepre():
        return '/battlepre/'

    @staticmethod
    def battledo(battleid):
        return '/battledo/%s' % battleid

    @staticmethod
    def battleanim():
        return '/battleanim/'

    @staticmethod
    def battleresultanim():
        return '/battleresultanim/'

    @staticmethod
    def battleresult():
        return '/battleresult/'

    @staticmethod
    def battleoppselect(post_cnt=0):
        return '/battleoppselect/%d/' % post_cnt

    @staticmethod
    def bprecover():
        return '/bprecover/'

    @staticmethod
    def gacha():
        return '/gacha'

    @staticmethod
    def gachado(mid, key):
        return '/gachado/%d/%s' % (mid, urllib.quote(key, ''))

    @staticmethod
    def gachapay():
        return '/gachapay'

    @staticmethod
    def gachaanim(mid, key):
        return '/gachaanim/%d/%s' % (mid, urllib.quote(key, ''))

    @staticmethod
    def gachaanimsub(mid):
        return '/gachaanimsub/%d/' % mid

    @staticmethod
    def gachaseatanim(mid, key):
        return '/gachaseatanim/%d/%s' % (mid, urllib.quote(key, ''))

    @staticmethod
    def gacharesult(mid, key, code=0, lottery_point=None):
        if lottery_point:
            return '/gacharesult/%d/%s/%d/%d' % (mid, urllib.quote(key, ''), code, lottery_point)
        else:
            return '/gacharesult/%d/%s/%d' % (mid, urllib.quote(key, ''), code)
    @staticmethod
    def gachamorecast(mid, key, code=0):
        return '/gachamorecast/%d/%s/%d' % (mid, urllib.quote(key, ''), code)

    @staticmethod
    def gachacardlist(mid):
        return '/gachacardlist/%d/' % mid

    @staticmethod
    def gachaboxreset(key):
        return '/gachaboxreset/%s' % urllib.quote(key, '')

    @staticmethod
    def gachaseatreset():
        return '/gachaseatreset/'

    @staticmethod
    def gachasupinfo(mid):
        return '/gachasupinfo/%d/' % mid

    @staticmethod
    def gachasupcard(mid, subbox=0):
        return '/gachasupcard/%d/%d/' % (mid, subbox)

    @staticmethod
    def gacharankingtop(mid):
        return '/gacharankingtop/%d/' % mid

    @staticmethod
    def gacharanking(mid, is_single, view_myrank):
        return '/gacharanking/%d/%d/%d/' % (mid, int(bool(is_single)), int(bool(view_myrank)))

    @staticmethod
    def gacharankingprize(mid, is_single, is_whole=False):
        return '/gacharankingprize/%d/%d/%d/' % (mid, int(bool(is_single)), int(bool(is_whole)))

    @staticmethod
    def gachaomakelist():
        return '/gachaomakelist/'

    @staticmethod
    def cardbox():
        return '/cardbox'

    @staticmethod
    def carddetail(cardid):
        return '/carddetail/%s' % cardid

    @staticmethod
    def cardprotect():
        return '/cardprotect'

    @staticmethod
    def deck(target='normal'):
        return '/deck/%s' % target

    @staticmethod
    def deck_raid():
        return UrlMaker.deck('raid')

    @staticmethod
    def deckset(auto=False, target='normal'):
        return '/deckset/%d/%s' % (int(auto), target)

    @staticmethod
    def deckmember(target='normal'):
        return '/deckmember/%s' % target

    @staticmethod
    def infomation():
        return '/infomation/list'

    @staticmethod
    def infomation_detail(mid):
        return '/infomation/detail/%d' % mid

    @staticmethod
    def playerlog(oid=None):
        if oid:
            return '/playerlog/%d' % oid
        else:
            return '/playerlog/'

    @staticmethod
    def friendlog(oid=None):
        if oid:
            return '/friendlog/%d' % oid
        else:
            return '/friendlog/'

    @staticmethod
    def composition():
        return '/composition'

    @staticmethod
    def compositionmaterial(baseid):
        return '/compositionmaterial/%d' % baseid

    @staticmethod
    def compositionyesno(baseid):
        return '/compositionyesno/%d' % baseid

    @staticmethod
    def compositiondo(baseid, key):
        return '/compositiondo/%d/%s' % (baseid, urllib.quote(key, ''))

    @staticmethod
    def compositionanim():
        return '/compositionanim'

    @staticmethod
    def compositionresult():
        return '/compositionresult'

    @staticmethod
    def evolution():
        return '/evolution'

    @staticmethod
    def evolutionmaterial(baseid):
        return '/evolutionmaterial/%d' % baseid

    @staticmethod
    def evolutionyesno(baseid):
        return '/evolutionyesno/%d' % baseid

    @staticmethod
    def evolutiondo(baseid, key):
        return '/evolutiondo/%d/%s' % (baseid, urllib.quote(key, ''))

    @staticmethod
    def evolutionanim():
        return '/evolutionanim'

    @staticmethod
    def evolutionresult():
        return '/evolutionresult'

    @staticmethod
    def transfer():
        return '/transfer/'

    @staticmethod
    def transferyesno():
        return '/transferyesno/'

    @staticmethod
    def transferdo(confirm_key):
        return '/transferdo/%s/' % urllib.quote(confirm_key, '')

    @staticmethod
    def transfercomplete():
        return '/transfercomplete/'

    @staticmethod
    def transferreturn(mid, confirm_key):
        return '/transferreturn/%d/%s/' % (mid, urllib.quote(confirm_key, ''))

    @staticmethod
    def transferreturncomplete(mid, num):
        return '/transferreturncomplete/%s/%s/' % (mid, num)

    @staticmethod
    def sell():
        return '/sell'

    @staticmethod
    def sellyesno():
        return '/sellyesno'

    @staticmethod
    def selldo():
        return '/selldo'

    @staticmethod
    def sellcomplete():
        return '/sellcomplete'

    @staticmethod
    def album():
        return '/album/'

    @staticmethod
    def memories():
        return '/memories'

    @staticmethod
    def albummovie(mid):
        return '/albummovie/%d/mov.m3u8' % mid

    @staticmethod
    def movie_keyget(mid):
        return '/movie/keyget/%s' % mid

    @staticmethod
    def friendlist():
        return '/friendlist'

    @staticmethod
    def friendsearch():
        return '/friendsearch'

    @staticmethod
    def friendrequest_auto():
        return '/friendrequest/auto'

    @staticmethod
    def friendrequest_yesno(fid):
        return '/friendrequest/yesno/%s' % fid

    @staticmethod
    def friendrequest_do():
        return '/friendrequest/do'

    @staticmethod
    def friendrequest_complete():
        return '/friendrequest/complete'

    @staticmethod
    def friendcancel_yesno(fid):
        return '/friendcancel/yesno/%s' % fid

    @staticmethod
    def friendcancel_do(fid):
        return '/friendcancel/do/%s' % fid

    @staticmethod
    def friendcancel_complete(fid):
        return '/friendcancel/complete/%s' % fid

    @staticmethod
    def friendreceive_yesno(fid, accept):
        return '/friendreceive/yesno/%s/%s' % (fid, int(accept))

    @staticmethod
    def friendreceive_do(fid, accept):
        return '/friendreceive/do/%s/%s' % (fid, int(accept))

    @staticmethod
    def friendreceive_complete(fid, accept):
        return '/friendreceive/complete/%s/%s' % (fid, int(accept))

    @staticmethod
    def friendremove_yesno(fid):
        return '/friendremove/yesno/%s' % fid

    @staticmethod
    def friendremove_do(fid):
        return '/friendremove/do/%s' % fid

    @staticmethod
    def friendremove_complete(fid):
        return '/friendremove/complete/%s' % fid

    @staticmethod
    def profile(uid):
        return '/profile/%s' % uid

    @staticmethod
    def greetlog(uid=''):
        return '/greetlog/%s' % uid

    @staticmethod
    def greet(uid):
        return '/greet/%s' % uid

    @staticmethod
    def greet_complete(uid, errcode, point_pre, point_post, logid):
        return '/greet_complete/%s/%s/%s/%s/%s' % (uid, errcode, point_pre, point_post, logid)

    @staticmethod
    def greet_comment_comp(uid, errcode, point_pre, point_post):
        return '/greet_comment_comp/%s/%s/%s/%s' % (uid, errcode, point_pre, point_post)

    @staticmethod
    def shop():
        return '/shop'

    @staticmethod
    def shopyesno(mid):
        return '/shopyesno/%d' % mid

    @staticmethod
    def shopdo(mid, key=''):
        return '/shopdo/%d/%s' % (mid, urllib.quote(key, ''))

    @staticmethod
    def shoppay():
        return '/shoppay'

    @staticmethod
    def shopresult(mid):
        return '/shopresult/%d' % mid

    @staticmethod
    def itemlist():
        return '/item_itemlist'

    @staticmethod
    def item_use(mid, prenum):
        return '/item_use/%s/%s' % (mid, prenum)

    @staticmethod
    def item_use2(mid, key):
        return '/item_use2/%s/%s' % (mid, urllib.quote(key, ''))

    @staticmethod
    def item_useyesno(mid):
        return '/item_useyesno/%s' % mid

    @staticmethod
    def item_usecomplete(mid, errcode, before_num, after_num, before_value, after_value):
        return '/item_usecomplete/%s/%s/%s/%s/%s/%s' % (mid, errcode, before_num, after_num, before_value, after_value)

    @staticmethod
    def albumdetail(albumid):
        return '/albumdetail/%s' % albumid

    @staticmethod
    def albummemories(mid):
        return '/albummemories/%s' % (mid)

    @staticmethod
    def present():
        return '/present/list'

    @staticmethod
    def presentdo():
        return '/present/do'

    @staticmethod
    def presentresult(over=False):
        return '/present/result/%d' % int(over)

    @staticmethod
    def treasurelist(treasuretype=''):
        return '/treasurelist/%s' % treasuretype

    @staticmethod
    def treasureget(treasuretype, treasureid=None):
        return '/treasureget/%s/%s' % (treasuretype, treasureid or '')

    @staticmethod
    def treasuregetcomplete(treasuretype, treasureid=None):
        return '/treasuregetcomplete/%s/%s' % (treasuretype, treasureid or '')

    @staticmethod
    def trade():
        return '/trade'

    @staticmethod
    def tradeyesno(mid):
        return '/tradeyesno/%s' % mid

    @staticmethod
    def tradedo(mid, key):
        return '/tradedo/%s/%s/' % (mid, urllib.quote(key, ''))

    @staticmethod
    def tradecomplete(mid):
        return '/tradecomplete/%s' % mid

    @staticmethod
    def tradeshop():
        return '/tradeshop'

    @staticmethod
    def tradeshopyesno(mid):
        return '/tradeshopyesno/%s' % mid

    @staticmethod
    def tradeshopdo(mid, key):
        return '/tradeshopdo/%s/%s/' % (mid, urllib.quote(key, ''))

    @staticmethod
    def tradeshopresult(mid):
        return '/tradeshopresult/%s' % mid

    @staticmethod
    def reprintticket_tradeshop(ticket_id=None):
        if ticket_id:
            return '/reprintticket_tradeshop/%s' % ticket_id
        else:
            return '/reprintticket_tradeshop/'

    @staticmethod
    def reprintticket_tradeshopyesno(mid):
        return '/reprintticket_tradeshopyesno/%s' % mid

    @staticmethod
    def reprintticket_tradeshopdo(mid, key):
        return '/reprintticket_tradeshopdo/%s/%s/' % (mid, urllib.quote(key, ''))

    @staticmethod
    def reprintticket_tradeshopresult(mid):
        return '/reprintticket_tradeshopresult/%s' % mid

    @staticmethod
    def loginbonus():
        return '/loginbonus'

    @staticmethod
    def loginbonusanim():
        return '/loginbonusanim'

    @staticmethod
    def loginbonustimelimiteddo():
        return '/lbtldo/'

    @staticmethod
    def loginbonustimelimitedanim(mid, loginbonus):
        return '/lbtlanim/%s/%s/' % (mid, int(bool(loginbonus)))

    @staticmethod
    def loginbonussugorokudo():
        return '/lbsugorokudo/'

    @staticmethod
    def loginbonussugorokuanim(mid, loginbonus):
        return '/lbsugorokuanim/%s/%s/' % (mid, int(bool(loginbonus)))

    @staticmethod
    def comebackanim(mid, loginbonus):
        return '/comebackanim/%s/%s/' % (mid, int(bool(loginbonus)))

    @staticmethod
    def teaser(mid):
        return '/teaser/%s/' % mid

    @staticmethod
    def help():
        return '/help/'

    @staticmethod
    def config():
        return '/config/'

    @staticmethod
    def serial_top(mid):
        return '/serial_top/%s/' % mid

    @staticmethod
    def serial_input(mid):
        return '/serial_input/%s/' % mid

    @staticmethod
    def support_paymentlist():
        return '/support_paymentlist/'

    @staticmethod
    def no_support():
        return '/no_support/'

    @staticmethod
    def session_error():
        return '/session_error/'

    #=============================================
    # レイドイベント.
    @staticmethod
    def raidevent_start():
        return '/raideventstart/'

    @staticmethod
    def raidevent_opening():
        return '/raideventopening/'

    @staticmethod
    def raidevent_epilogue():
        return '/raideventepilogue/'

    @staticmethod
    def raidevent_bigboss():
        return '/raideventbigboss/'

    @staticmethod
    def raidevent_timebonus():
        return '/raideventtimebonus/'

    @staticmethod
    def raidevent_top(mid=None):
        if mid is None:
            return '/raideventtop/'
        else:
            return '/raideventtop/%d/' % mid

    @staticmethod
    def raidevent_gachacast(mid):
        return '/raideventgachacast/%d/' % mid

    @staticmethod
    def raidevent_explain(mid, ope='detail'):
        return '/raideventexplain/%d/%s/' % (mid, ope)

    @staticmethod
    def raidevent_ranking(mid, myrank=False):
        return '/raideventranking/%d/%d/' % (mid, int(bool(myrank)))

    @staticmethod
    def raidevent_battlepre():
        return '/raideventbattlepre/'

    @staticmethod
    def raidevent_helplist():
        return '/raideventhelplist/'

    @staticmethod
    def raidevent_prizereceive_do(mid, key):
        return '/raideventprizereceive/do/%s/%s/' % (mid, urllib.quote(key, safe=''))

    @staticmethod
    def raidevent_prizereceive_anim(mid):
        return '/raideventprizereceive/anim/%s/' % mid

    @staticmethod
    def raidevent_prizereceive_complete(mid):
        return '/raideventprizereceive/complete/%s/' % mid

    @staticmethod
    def raidevent_recipe_list():
        return '/raideventrecipelist/'

    @staticmethod
    def raidevent_recipe_yesno(recipeid):
        return '/raideventrecipeyesno/%d/' % recipeid

    @staticmethod
    def raidevent_recipe_do(recipeid, key):
        return '/raideventrecipedo/%d/%s/' % (recipeid, urllib.quote(key, ''))

    @staticmethod
    def raidevent_recipe_complete(recipeid):
        return '/raideventrecipecomplete/%d/' % recipeid

    @staticmethod
    def raidevent_scouttop():
        return '/raideventscouttop/'

    @staticmethod
    def raidevent_scoutdo(scoutid, key):
        return '/raideventscoutdo/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def raidevent_scoutanim(scoutid, key):
        return '/raideventscoutanim/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def raidevent_scoutresultanim(scoutid, key, idx):
        return '/raideventscoutresultanim/%d/%s/%d' % (scoutid, urllib.quote(key, ''), idx)

    @staticmethod
    def raidevent_scoutresult(scoutid, key):
        return '/raideventscoutresult/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def raidevent_scoutcardget(scoutid):
        return '/raideventscoutcardget/%d/' % scoutid

    @staticmethod
    def raidevent_scoutcardgetresult(scoutid):
        return '/raideventscoutcardgetresult/%d/' % scoutid

    @staticmethod
    def raidevent_scenarioanim(stageid, battlekey):
        return UrlMaker.bossscenarioanim(stageid, battlekey)

    #=============================================
    # プロデュースイベント.
    @staticmethod
    def produceevent_top(mid=None):
        if mid is None:
            return '/produceeventtop/'
        else:
            return '/produceeventtop/%d/' % mid

    @staticmethod
    def produceevent_explain(mid, ope='detail'):
        return '/produceeventexplain/%d/%s/' % (mid, ope)

    @staticmethod
    def produceevent_scouttop():
        return '/produceeventscouttop/'

    @staticmethod
    def produceevent_ranking(mid, myrank=False):
        return '/produceeventranking/%d/%d/' % (mid, int(bool(myrank)))

    @staticmethod
    def produceevent_scoutdo(scoutid, key):
        return '/produceeventscoutdo/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def produceevent_scoutresult(scoutid, key):
        return '/produceeventscoutresult/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def produceevent_battlepre():
        return '/produceeventbattlepre/'

    @staticmethod
    def produceevent_raidresultanim(raidid=''):
        if raidid:
            return '/produceraid/resultanim/%d/' % raidid
        else:
            return '/produceraid/resultanim/'

    @staticmethod
    def produceevent_raidend(raidid):
        return '/produceraid/end/%s/' % raidid

    @staticmethod
    def producehappening():
        return '/producehappening'

    @staticmethod
    def producehappeningdo(key):
        return '/producehappeningdo/%s' % urllib.quote(key, '')

    @staticmethod
    def producehappeninganim(key):
        return '/producehappeninganim/%s' % urllib.quote(key, '')

    @staticmethod
    def producehappeningresultanim(key, idx=0):
        return '/producehappeningresultanim/%s/%d' % (urllib.quote(key, ''), idx)

    @staticmethod
    def producehappeningresult(key):
        return '/producehappeningresult/%s' % urllib.quote(key, '')

    @staticmethod
    def producehappeningend(happeningid):
        return '/producehappeningend/%s/' % happeningid

    @staticmethod
    def produceraiddo(raidid, key):
        return '/produceraid/do/%s/%s/' % (raidid, urllib.quote(key, ''))

    @staticmethod
    def produceraidresult():
        return '/produceraid/result/'

    @staticmethod
    def produceraidend(raidid):
        return '/produceraid/end/%s/' % raidid

    @staticmethod
    def produceraidanim():
        return '/produceraid/anim/'

    @staticmethod
    def produceraidresultanim(raidid=''):
        if raidid:
            return '/produceraid/resultanim/%d/' % raidid
        else:
            return '/produceraid/resultanim/'

    @staticmethod
    def produceraidrarityanim(new_order, old_order):
        return '/produceraid/rarityanim/%d/%d/' % (new_order, old_order)

    @staticmethod
    def produceraidlastcastgetanim(cardid):
        return '/produceraid/lastcastgetanim/%d/' % cardid

    @staticmethod
    def produceevent_scoutresultanim(scoutid, key, idx):
        return '/produceeventscoutresultanim/%d/%s/%d' % (scoutid, urllib.quote(key, ''), idx)

    @staticmethod
    def produceevent_scoutanim(scoutid, key):
        return '/produceeventscoutanim/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def produceevent_opening():
        return '/produceeventopening/'

    @staticmethod
    def produceevent_epilogue():
        return '/produceeventepilogue/'

    @staticmethod
    def produceevent_scoutcardget(scoutid):
        return '/produceeventscoutcardget/%d/' % scoutid

    @staticmethod
    def produceevent_scoutcardgetresult(scoutid):
        return '/produceeventscoutcardgetresult/%d/' % scoutid

    @staticmethod
    def produceevent_scenarioanim(stageid, battlekey):
        return UrlMaker.bossscenarioanim(stageid, battlekey)

    #=============================================
    @staticmethod
    def ban():
        return '/ban/'

    #=============================================
    # スカウトイベント.
    @staticmethod
    def scoutevent_opening():
        return '/sceventopening/'

    @staticmethod
    def scoutevent_epilogue():
        return '/sceventepilogue/'

    @staticmethod
    def scoutevent_start():
        return '/sceventstart/'

    @staticmethod
    def scoutevent_top(mid=None):
        if mid is None:
            return '/sceventtop/'
        else:
            return '/sceventtop/%d/' % mid

    @staticmethod
    def scoutevent_ranking(mid, myrank=False):
        return '/sceventranking/%s/%s/' % (mid, int(bool(myrank)))

    @staticmethod
    def scoutevent_explain(mid, ope='detail'):
        return '/sceventexplain/%d/%s/' % (mid, ope)

    @staticmethod
    def scouteventareamap():
        return '/sceventareamap/'

    @staticmethod
    def scoutevent():
        return '/scevent/'

    @staticmethod
    def scouteventdo(scoutid, key):
        return '/sceventdo/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scouteventanim(scoutid, key):
        return '/sceventanim/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scouteventresultanim(scoutid, key, idx):
        return '/sceventresultanim/%d/%s/%d' % (scoutid, urllib.quote(key, ''), idx)

    @staticmethod
    def scouteventresult(scoutid, key):
        return '/sceventresult/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scouteventcardget(scoutid):
        return '/sceventcardget/%d/' % scoutid

    @staticmethod
    def scouteventcardgetresult(scoutid):
        return '/sceventcardgetresult/%d/' % scoutid

    @staticmethod
    def scouteventfever(scoutid, key):
        return '/sceventfever/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scouteventscenarioanim(stageid, battlekey):
        return UrlMaker.bossscenarioanim(stageid, battlekey)

    @staticmethod
    def scoutevent_movie(stage=None):
        return '/sceventmovie/%s' % ('' if stage is None else stage)

    @staticmethod
    def scouteventproduce():
        return '/sceventproduce/'

    @staticmethod
    def scouteventlovetime(scoutid, key):
        return '/sceventlovetime/%d/%s' % (scoutid, urllib.quote(key, ''))

    @staticmethod
    def scouteventcastnomination():
        return '/sceventcastnomination/'

    @staticmethod
    def scouteventtippopulatecomplete(tanzaku_number, tip):
        return '/sceventtippopulatecomplete/{}/{}/'.format(tanzaku_number, tip)

    @staticmethod
    def scouteventtiptrade():
        return '/sceventtiptrade/'

    @staticmethod
    def scouteventtiptradedo(confirmkey):
        return '/sceventtiptradedo/{}/'.format(urllib.quote(confirmkey, ''))

    @staticmethod
    def scouteventtiptraderesult(tanzaku_number, tanzaku_num):
        return '/sceventtiptraderesult/{}/{}/'.format(tanzaku_number, tanzaku_num)

    #=============================================
    # バトルイベント.
    @staticmethod
    def battleevent_teaser(mid=None):
        return '/battleeventteaser/%s' % (mid or '')

    @staticmethod
    def battleevent_opening():
        return '/battleeventopening/'

    @staticmethod
    def battleevent_epilogue():
        return '/battleeventepilogue/'

    @staticmethod
    def battleevent_scenario():
        return '/battleeventscenario/'

    @staticmethod
    def battleevent_regist():
        return '/battleeventregist/'

    @staticmethod
    def battleevent_loginbonus():
        return '/battleeventloginbonus/'

    @staticmethod
    def battleevent_loginbonusanim(eventid, fame, fame_next, rank, rank_next, grouprank):
        return '/battleeventloginbonusanim/%s/%s/%s/%s/%s/%s/' % (eventid, fame, fame_next, rank, rank_next, grouprank)

    @staticmethod
    def battleevent_top(mid=None):
        if mid is None:
            return '/battleeventtop/'
        else:
            return '/battleeventtop/%d/' % mid

    @staticmethod
    def battleevent_opplist(target='lv', do_update=False):
        return '/battleeventopplist/%s/%s/' % (target, int(bool(do_update)))

    @staticmethod
    def battleevent_battlepre(oid, revengeid=None, rival_key=None):
        str_list = [revengeid, rival_key]
        url = '/battleeventbattlepre/%s/' % oid
        for strings in str_list:
            if revengeid:
                url = '%s%s/' % (url, revengeid)
            if rival_key:
                url = '%s%s/' % (url, rival_key)
        return url

    @staticmethod
    def battleevent_battledo(confirmkey, oid, revengeid=None, rival_key=None):
        str_list = [revengeid, rival_key]
        url = '/battleeventbattledo/%s/%s/' %  (urllib.quote(confirmkey, ''), oid)
        for strings in str_list:
            if revengeid:
                url = '%s%s/' % (url, revengeid)
            if rival_key:
                url = '%s%s/' % (url, rival_key)
        return url

    @staticmethod
    def battleevent_battleanim(eventid):
        url = '/battleeventbattleanim/%s/' % eventid
        return url

    @staticmethod
    def battleevent_battlepiecepresent(eventid, rarity=None, piecenumber=None, is_complete=None):
        url = '/battleeventbattlepiecepresent/%s/' % eventid
        if (not rarity is None) and (not piecenumber is None):
            url = '%s%s/%s/' % (url, rarity, piecenumber)
        if is_complete:
            return '%s%s/' % (url, 1)
        else:
            return url

    @staticmethod
    def battleevent_battleresultanim(eventid, rarity=None, piecenumber=None, is_complete=None):
        if (not rarity is None) and (not piecenumber is None):
            url = '/battleeventresultanim/%s/%s/%s/' % (eventid, rarity, piecenumber)
        else:
            url = '/battleeventresultanim/%s/' % eventid
        if is_complete:
            url = '%s%s' % (url, 1)
        return url

    @staticmethod
    def battleevent_battleresult(eventid, rarity=None, piecenumber=None):
        if (not rarity is None) and (not piecenumber is None):
            return '/battleeventbattleresult/%s/%s/%s/' % (eventid, rarity, piecenumber)
        else:
            return '/battleeventbattleresult/%s/' % eventid

    @staticmethod
    def battleevent_ranking(mid, myrank=False):
        return '/battleeventranking/%s/%s/' % (mid, int(bool(myrank)))

    @staticmethod
    def battleevent_loglist():
        return '/battleeventloglist/'

    @staticmethod
    def battleevent_grouploglist(eventid):
        return '/battleeventgrouplog/list/%s/' % eventid

    @staticmethod
    def battleevent_grouplogdetail(groupid):
        return '/battleeventgrouplog/detail/%s/' % groupid

    @staticmethod
    def battleevent_groupdetail(groupid):
        return '/battleeventgroupdetail/%s/' % groupid

    @staticmethod
    def battleevent_group():
        return '/battleeventgroup/'

    @staticmethod
    def battleevent_explain(mid, ope='detail'):
        return '/battleeventexplain/%d/%s/' % (mid, ope)

    @staticmethod
    def battleevent_present():
        return '/battleeventpresent/'

    @staticmethod
    def battleevent_presentreceive(confirmkey):
        return '/battleeventpresentreceive/%s/' % urllib.quote(confirmkey, '')

    @staticmethod
    def battleevent_presentanim():
        return '/battleeventpresentanim/'

    @staticmethod
    def battleevent_presentlist():
        return '/battleeventpresentlist/'

    #=============================================
    # クロスプロモーション.
    @staticmethod
    def promotion_top(appname):
        return '/promotiontop/%s/' % appname

    @staticmethod
    def promotion_prizelist(appname):
        return '/promotionprize/list/%s/' % appname

    @staticmethod
    def promotion_prizereceive_yesno(appname, mid):
        return '/promotionprize/receiveyesno/%s/%s/' % (appname, mid)

    @staticmethod
    def promotion_prizereceive_do(appname, mid):
        return '/promotionprize/receivedo/%s/%s/' % (appname, mid)

    @staticmethod
    def promotion_prizereceive_complete(appname, mid):
        return '/promotionprize/receivecomplete/%s/%s/' % (appname, mid)

    @staticmethod
    def panelmissiontop():
        return '/panelmissiontop/'

    @staticmethod
    def panelmissionanim(panel):
        return '/panelmissionanim/%s/' % panel

    @staticmethod
    def popupview(mid):
        return '/popupview/%s/' % mid

    #=============================================
    # Effect.
    @staticmethod
    def event_scenario():
        return 'event_scenario4/effect2.html'

    #=============================================
    # 経営.
    @staticmethod
    def cabaclubtop():
        return '/cabaclubtop/'
    
    @staticmethod
    def cabaclubresultanim():
        return '/cabaclubresultanim/'
    
    @staticmethod
    def cabaclubeventanim(mid):
        return '/cabaclubeventanim/%s/' % mid

    @staticmethod
    def cabaclubrank(mid, ope=None):
        if ope:
            return '/cabaclubrank/%s/%s/' % (mid, ope)
        return '/cabaclubrank/%s/' % (mid)


    @staticmethod
    def cabaclubstore(mid=None):
        return '/cabaclubstore/%s' % (mid or '')
    
    @staticmethod
    def cabaclubrentyesno(mid):
        return '/cabaclubrentyesno/%s/' % mid
    
    @staticmethod
    def cabaclubrentdo(mid):
        return '/cabaclubrentdo/%s/' % mid
    
    @staticmethod
    def cabaclubrentend(mid):
        return '/cabaclubrentend/%s/' % mid
    
    @staticmethod
    def cabaclubopen(mid):
        return '/cabaclubopen/%s/' % mid
    
    @staticmethod
    def cabaclubclose(mid):
        return '/cabaclubclose/%s/' % mid
    
    @staticmethod
    def cabaclubuayesno(mid):
        return '/cabaclubuayesno/%s/' % mid
    
    @staticmethod
    def cabaclubuado(mid):
        return '/cabaclubuado/%s/' % mid
    
    @staticmethod
    def cabaclubuaend(mid):
        return '/cabaclubuaend/%s/' % mid
    
    @staticmethod
    def cabaclubcancelyesno(mid):
        return '/cabaclubcancelyesno/%s/' % mid
    
    @staticmethod
    def cabaclubcanceldo(mid):
        return '/cabaclubcanceldo/%s/' % mid
    
    @staticmethod
    def cabaclubcancelend(mid):
        return '/cabaclubcancelend/%s/' % mid
    
    @staticmethod
    def cabaclubcastselect(mid, cardid=None):
        return '/cabaclubcastselect/%s/%s' % (mid, cardid or '')
    
    @staticmethod
    def cabaclubcastselectdo(mid, cardid_remove, cardid_add):
        return '/cabaclubcastselectdo/%s/%s/%s/' % (mid, cardid_remove or 0, cardid_add)
    
    @staticmethod
    def cabaclubcastremove(mid, cardid):
        return '/cabaclubcastremove/%s/%s/' % (mid, cardid)

    @staticmethod
    def cabaclubdeckselect(mid):
        return '/cabaclubdeckselect/%s/' % mid
    
    #=============================================
    # 称号.
    @staticmethod
    def titletop():
        return '/titletop/'
    
    @staticmethod
    def titleyesno(mid):
        return '/titleyesno/%s/' % mid
    
    @staticmethod
    def titledo(mid):
        return '/titledo/%s/' % mid
    
    @staticmethod
    def titleend(mid):
        return '/titleend/%s/' % mid
    
    
    #=============================================
    # Admin.
    @staticmethod
    def index():
        return '/'

    @staticmethod
    def login():
        return '/login'

    @staticmethod
    def logout():
        return '/logout'

    @staticmethod
    def model_edit(name, *args):
        return '/model_edit/%s/%s' % (name, '/'.join([str(v) for v in args]))

    @staticmethod
    def mgr_infomations(name, *args):
        return '/infomations/%s/%s' % (name, '/'.join([str(v) for v in args]))

    @staticmethod
    def mgr_kpi(name, *args):
        return '/kpi/%s/%s' % (name, '/'.join([str(v) for v in args]))

    @staticmethod
    def mgr_simulator(name, *args):
        return '/simulator/%s/%s' % (name, '/'.join([str(v) for v in args]))

    @staticmethod
    def view_images():
        return '/view_images/'

    @staticmethod
    def view_player(uid=None):
        return '/infomations/view_player/%s' % (uid or '')

    @staticmethod
    def view_raid(raidid=None):
        return '/infomations/view_raid/%s' % (raidid or '')

    @staticmethod
    def view_raidlog():
        return '/infomations/view_raidlog/'

    @staticmethod
    def view_battleevent_group(groupid=None):
        return '/infomations/view_battleevent_group/%s' % (groupid or '')

    @staticmethod
    def view_battleevent_battlelog():
        return '/infomations/view_battleevent_battlelog/'

    @staticmethod
    def view_promotion(dmmid):
        return '/infomations/view_promotion/%s/' % dmmid

    @staticmethod
    def view_serialcode():
        return '/infomations/view_serialcode/'

    @staticmethod
    def view_paymentlog():
        return '/infomations/view_paymentlog/'

    @staticmethod
    def view_eventranking():
        return '/infomations/view_eventranking/'

    @staticmethod
    def view_panelmission(uid=None):
        return '/infomations/view_panelmission/%s' % (uid or '')

    @staticmethod
    def ban_edit(ope='list'):
        return '/ban_edit/%s/' % ope

    @staticmethod
    def master_data(proc=''):
        return '/master_data/%s' % proc

    @staticmethod
    def movie_edit():
        return '/movie/'

    @staticmethod
    def voice_edit():
        return '/voice/'

    @staticmethod
    def ng_cast(ope='list'):
        return '/ng_cast/%s/' % ope

    @staticmethod
    def apitest():
        return '/apitest'

    @staticmethod
    def getstatus():
        return '/getstatus'

    @staticmethod
    def swf(path):
        return '/swf/%s' % path
