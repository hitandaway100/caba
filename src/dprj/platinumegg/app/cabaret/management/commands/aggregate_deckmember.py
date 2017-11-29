# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
import datetime
from platinumegg.app.cabaret.util.redisdb import LoginTimeCloneSet
from platinumegg.app.cabaret.models.Card import Deck, Card, CardMaster,\
    CardSortMaster
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.lib.strutil import StrUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """アクティブユーザーのデッキ情報.
    """
    class Writer():
        def __init__(self, path, keep_maxlength=50000):
            self._path = path
            self._size = 0
            self._data = []
            self._keep_maxlength = keep_maxlength
            self.output(overwrite=True)
        
        def add(self, text):
            print text
            self._data.append(text)
            self._size += len(text)     # 厳密には違うけど..
            if self._keep_maxlength <= self._size:
                self.output(overwrite=False)
                self._data = []
                self._size = 0
        
        def output(self, overwrite=False):
            if self._data:
                self._data.append('\n')
            data_str = StrUtil.to_s('\n'.join(self._data), 'shift-jis')
            if overwrite:
                mode = 'w'
            else:
                mode = 'a'
            f = None
            try:
                f = open(self._path, mode)
                f.write(data_str)
                f.close()
            except:
                if f:
                    f.close()
                raise
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'aggregate_deckmember'
        print '================================'
        
        # 出力先.
        path = OSAUtil.get_now().strftime(args[0])
        
        # 書き込むデータをここに溜め込む.
        writer = Command.Writer(path)
        
        # 対象を更新.
        LoginTimeCloneSet.update()
        
        # アクティブユーザだと判定される日数.
        now = OSAUtil.get_now()
        border_date = now - datetime.timedelta(days=Defines.ACTIVE_DAYS)
        
        LIMIT = 300
        
        model_mgr = ModelRequestMgr()
        cardmasters = dict([(master.id, master) for master in model_mgr.get_mastermodel_all(CardMaster, fetch_deleted=True, using=backup_db)])
        cardsortmasters = dict([(master.id, master) for master in model_mgr.get_mastermodel_all(CardSortMaster, fetch_deleted=True, using=backup_db)])
        
        # ヘッダ列.
        title = [u'ユーザID']
        for _ in xrange(Defines.DECK_CARD_NUM_MAX):
            title.extend([u'name', u'rare', u'hklevel', u'level', u'power'])
        for rare in Defines.Rarity.LIST:
            title.append(Defines.Rarity.NAMES[rare])
        writer.add(','.join(title))
        del title
        
        offset = 0
        while True:
            uidlist = LoginTimeCloneSet.fetchByRange(border_date, now, LIMIT, offset)
            
            # デッキ取得.
            decklist = Deck.getByKey(uidlist, using=backup_db)
            
            for deck in decklist:
                row = []
                
                raremap = {}
                
                # カード取得.
                cardidlist = deck.to_array()
                cards = dict([(card.id, card) for card in Card.getByKey(cardidlist, using=backup_db)])
                
                # ユーザID.
                row.append(str(deck.id))
                
                for cardid in cardidlist:
                    card = cards.get(cardid)
                    master = None
                    sortmaster = None
                    if card:
                        master = cardmasters.get(card.mid)
                        sortmaster = cardsortmasters.get(card.mid)
                    
                    if card is None or master is None or sortmaster is None:
                        name = u'不明'
                        rare = u'不明'
                        hklevel = u'不明'
                        level = u'不明'
                        power = u'不明'
                    else:
                        # カード名.
                        name = str(master.name)
                        # レア度.
                        rare = str(sortmaster.rare)
                        # ハメ管理度.
                        hklevel = str(sortmaster.hklevel)
                        # レベル.
                        level = str(card.level)
                        # 接客力.
                        power = str(CardUtil.calcPower(master.gtype, master.basepower, master.maxpower, card.level, master.maxlevel, card.takeover))
                        
                        raremap[sortmaster.rare] = raremap.get(sortmaster.rare, 0) + 1
                    
                    row.extend([name, rare, hklevel, level, power])
                
                for _ in xrange(Defines.DECK_CARD_NUM_MAX - len(cardidlist)):
                    row.extend(['', '', '', '', ''])
                
                for rare in Defines.Rarity.LIST:
                    row.append(str(raremap.get(rare, 0)))
                
                line = ','.join(row)
                writer.add(line)
            
            offset += LIMIT
            
            if len(uidlist) < LIMIT:
                break
        
        writer.output(overwrite=False)
        
        print '================================'
        print 'all done..'
    
