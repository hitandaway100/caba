# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.models.Card import CardMaster
import settings
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.alert import AlertCode
from defines import Defines
from platinumegg.app.cabaret.util.card import CardSet
from platinumegg.app.cabaret.util.apprandom import AppRandom

class Handler(AdminHandler):
    """PVPのシミュレータ.
    """
    def process(self):
        
        self.__flag_execute = self.request.get('_execute') == '1'
        self.__vid = self.request.get('_vid')
        self.__oid = self.request.get('_oid')
        self.__v_deck = None
        self.__o_deck = None
        self.__continuity = self.request.get('_continuity')
        self.__dummy_cardid = 0
        
        model_mgr = self.getModelMgr()
        
        # カード一覧.
        cardmidlist = [cardmaster.id for cardmaster in model_mgr.get_mastermodel_all(CardMaster, 'id', using=settings.DB_READONLY)]
        cardmaster_all = BackendApi.get_cardmasters(cardmidlist, model_mgr, using=settings.DB_READONLY)
        obj_cardlist = [Objects.cardmaster(self, cardmaster_all[mid]) for mid in cardmidlist]
        self.html_param['cardlist'] = obj_cardlist
        
        # 個別設定されたデッキ.
        self.loadPostDeck()
        
        # ユーザIDからロード.
        self.loadUserDeck()
        
        # 対戦する.
        if self.__flag_execute:
            self.battle()
        
        self.putDeck()
        
        self.html_param['vid'] = self.__vid
        self.html_param['oid'] = self.__oid
        self.html_param['continuity'] = self.__continuity or 10
        self.writeAppHtml('battle_simulator')
    
    def createDummyCard(self, master):
        self.__dummy_cardid += 1
        card = BackendApi.create_card_by_master(master)
        card.id = self.__dummy_cardid
        return card
    
    def loadUserDeck(self):
        """ユーザのデッキのロード.
        """
        if self.__flag_execute:
            return
        
        model_mgr = self.getModelMgr()
        def get(uid):
            if not uid:
                return None
            elif not uid.isdigit() or int(uid) < 1:
                self.putAlertToHtmlParam(u'ユーザIDは自然数で指定してください', AlertCode.ERROR)
                return None
            uid = int(uid)
            deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_READONLY)
            cardidlist = deck.to_array()
            if not cardidlist:
                self.putAlertToHtmlParam(u'存在しないユーザーです.id=%s' % uid, AlertCode.ERROR)
                return None
            return BackendApi.get_cards(deck.to_array(), model_mgr, using=settings.DB_READONLY)
        self.__v_deck = get(self.__vid) or self.__v_deck
        self.__o_deck = get(self.__oid) or self.__o_deck
    
    def loadPostDeck(self):
        """ポストされたのデッキのロード.
        """
        KEY_FORMAT = '{prefix}_{number}_{param}'
        model_mgr = self.getModelMgr()
        def get(prefix):
            deck = []
            for i in xrange(Defines.DECK_CARD_NUM_MAX):
                mid = self.request.get(KEY_FORMAT.format(prefix=prefix, number=i, param='mid'))
                if mid:
                    mid = int(mid)
                    level = int(self.request.get(KEY_FORMAT.format(prefix=prefix, number=i, param='level')))
                    takeover = int(self.request.get(KEY_FORMAT.format(prefix=prefix, number=i, param='takeover')))
                    skilllevel = int(self.request.get(KEY_FORMAT.format(prefix=prefix, number=i, param='skilllevel')))
                    cardmaster = BackendApi.get_cardmasters([mid], model_mgr, using=settings.DB_READONLY).get(mid)
                    card = self.createDummyCard(cardmaster)
                    card.level = max(1, min(cardmaster.maxlevel, level))
                    card.takeover = max(0, takeover)
                    card.skilllevel = max(1, min(Defines.SKILLLEVEL_MAX, skilllevel))
                    deck.append(CardSet(card, cardmaster))
            return deck
        self.__v_deck = get('v_deck')
        self.__o_deck = get('o_deck')
    
    def putDeck(self):
        """ロードしたデッキを埋め込む.
        """
        if self.__v_deck:
            self.html_param['v_deck'] = [Objects.card(self, cardset) for cardset in self.__v_deck]
        if self.__o_deck:
            self.html_param['o_deck'] = [Objects.card(self, cardset) for cardset in self.__o_deck]
    
    def battle(self):
        """対戦する.
        """
        continuity = 0
        if self.__continuity and self.__continuity.isdigit():
            continuity = int(self.__continuity)
        continuity = min(1000, max(1, continuity))
        
        v_carddict = dict([(cardset.id, cardset) for cardset in self.__v_deck])
        o_carddict = dict([(cardset.id, cardset) for cardset in self.__o_deck])
        
        def skillinfoToText(skillinfo):
            if skillinfo.playerFlag:
                cardset = v_carddict[skillinfo.skillUseCardId]
            else:
                cardset = o_carddict[skillinfo.skillUseCardId]
            return u'{skillname} Lv{skilllevel}'.format(skillname=skillinfo.skillName, skilllevel=cardset.card.skilllevel)
        
        # カードごとにどれだけスキルを発動していて発動した時のどれだけ勝っているか.
        v_cardSkillCounts = {}
        o_cardSkillCounts = {}
        
        def addSkillCount(skillinfo, is_win):
            if skillinfo.playerFlag:
                cardSkillCounts = v_cardSkillCounts
            else:
                cardSkillCounts = o_cardSkillCounts
                is_win = not is_win
            cardid = skillinfo.skillUseCardId
            data = cardSkillCounts[cardid] = cardSkillCounts.get(cardid, {'win':0, 'count':0})
            data['count'] += 1
            if is_win:
                data['win'] += 1
        
        win = 0
        feverWin = 0
        feverCnt = 0
        results = []
        for i in xrange(continuity):
            resultdata, animdata = BackendApi.battle(None, self.__v_deck, None, self.__o_deck, AppRandom())
            
            is_win = resultdata['is_win']
            
            pSkill = []
            eSkill = []
            for skillinfolist, skilltextlist in ((animdata.pSkill, pSkill), (animdata.eSkill, eSkill)):
                for skillinfo in skillinfolist:
                    skilltextlist.append(skillinfoToText(skillinfo))
                    addSkillCount(skillinfo, is_win)
            
            if i < 100:
                resultdata.update({
                    'fever' : animdata.feverFlag,
                    'pSale' : animdata.pSale,
                    'eSale' : animdata.eSale,
                    'pSkill' : pSkill,
                    'eSkill' : eSkill,
                })
                results.append(resultdata)
            
            if is_win:
                win += 1
            if animdata.feverFlag:
                if is_win:
                    feverWin += 1
                feverCnt += 1
        
        self.html_param['battleresult'] = {
            'win' : win,
            'feverCnt' : feverCnt,
            'feverWin' : feverWin,
            'continuity' : continuity,
            'resultlist' : results,
            'v_cardSkillCounts' : v_cardSkillCounts,
            'o_cardSkillCounts' : o_cardSkillCounts,
        }
    

def main(request):
    return Handler.run(request)
