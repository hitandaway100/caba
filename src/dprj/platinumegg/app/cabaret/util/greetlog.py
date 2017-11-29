# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import Player
import settings
from platinumegg.lib.platform.api.objects import PeopleRequestData
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Card import Deck, Card, CardMaster
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.lib.platform.api.objects import InspectionGetRequestData


class GreetLogData:
    """あいさつ履歴.
    """
    def __init__(self, log_data=None):
        if log_data:
            self.id = log_data.id
            self.fromid = log_data.fromid
            self.toid = log_data.toid
            self.gtime = log_data.gtime
            self.commenttextid = log_data.commenttextid
        else:
            self.id = 0
            self.fromid = 0
            self.toid = 0
            self.gtime = OSAUtil.get_now()
            self.commenttextid = u''
        self.params = {}
        self.__db_data = log_data
    
    def makePersonApiRequest(self, apphandler):
        """表示用に必要な情報をロード.
        """
        model_mgr = apphandler.getModelMgr()
        player = model_mgr.get_model(Player, self.fromid, using=settings.DB_READONLY)
        if player is None:
            return None
        data = PeopleRequestData.createForPeople(player.dmmid)
        request = apphandler.osa_util.makeApiRequest(ApiNames.People, data)
        return request
    
    def load(self, apphandler):
        """表示用に必要な情報をロード.
        """
        key = 'GreetLog:fromid:%s' % self.id
        key_comment = 'GreetLogComment:fromid:%s' % self.id
        
        def cb(ret_data, *args, **kwargs):
            try:
                person = ret_data[key].get()
                self.params['dmmid'] = person.id
                self.params['username'] = person.nickname
            except:
                self.params['dmmid'] = ''
                self.params['username'] = u'****'
        
        self.params['url'] = apphandler.makeAppLinkUrl(UrlMaker.profile(self.fromid))
        
        # Personとか欲しいはず.
        request = self.makePersonApiRequest(apphandler)
        apphandler.addAppApiRequest(key, request, cb)
        
        # サムネ.
        model_mgr = apphandler.getModelMgr()
        deck = model_mgr.get_model(Deck, self.fromid, using=settings.DB_READONLY)
        leader = model_mgr.get_model(Card, deck.leader, using=settings.DB_READONLY)
        master = model_mgr.get_model(CardMaster, leader.mid, using=settings.DB_READONLY)
        self.params['thumbUrl'] = apphandler.makeAppLinkUrlImg(CardUtil.makeThumbnailUrlIcon(master))
        
        if self.commenttextid != '':
            def cb_comment(ret_data, *args, **kwargs):
                try:
                    result = ret_data[key_comment].get()
                    if len(result) == 1:
                        status = result[0].status
                        data = result[0].data
                        self.params['comment'] = data
                    else:
                        self.params['comment'] = u''
                except:
                    self.params['comment'] = u'********'
            
            data = InspectionGetRequestData()
            data.textId = self.commenttextid
            
            request = apphandler.osa_util.makeApiRequest(ApiNames.InspectionGet, data)
            apphandler.addAppApiRequest(key_comment, request, cb_comment)
        else:
            self.params['comment'] = u''
        
