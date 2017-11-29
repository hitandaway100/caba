# -*- coding: utf-8 -*-
from defines import Defines



class ItemUtil:
    """アイテム関係.
    """
    @staticmethod
    def makeThumbnailUrlSmallByDBString(thumb):
        """60*60サムネ画像.
        """
        if thumb:
            return u'%s/Item_thumb_60_60.png' % thumb
        else:
            return u'common/item.png'
    
    @staticmethod
    def makeThumbnailUrlMiddleByDBString(thumb):
        """90*90サムネ画像.
        """
        if thumb:
            return u'%s/Item_thumb_90_90.png' % thumb
        else:
            return u'common/item.png'
    
    @staticmethod
    def makeThumbnailUrlSmall(master):
        """60*60サムネ画像.
        """
        return ItemUtil.makeThumbnailUrlSmallByDBString(master.thumb)
    
    @staticmethod
    def makeThumbnailUrlMiddle(master):
        """90*90サムネ画像.
        """
        return ItemUtil.makeThumbnailUrlMiddleByDBString(master.thumb)
    
    @staticmethod
    def makeThumbnailUrlSmallByType(itemtype):
        """60*60サムネ画像.
        """
        thumb = Defines.ItemType.THUMBNAIL.get(itemtype)
        return ItemUtil.makeThumbnailUrlSmallByDBString(thumb)
    
    @staticmethod
    def makeThumbnailUrlMiddleByType(itemtype):
        """90*90サムネ画像.
        """
        thumb = Defines.ItemType.THUMBNAIL.get(itemtype)
        return ItemUtil.makeThumbnailUrlMiddleByDBString(thumb)
    
    @staticmethod
    def makeThumbnailUrlSmallByTreasureType(itemtype):
        """60*60サムネ画像.
        """
        thumb = Defines.TreasureType.THUMBNAIL.get(itemtype)
        return ItemUtil.makeThumbnailUrlSmallByDBString(thumb)
    
    @staticmethod
    def makeThumbnailUrlMiddleByTreasureType(itemtype):
        """90*90サムネ画像.
        """
        thumb = Defines.TreasureType.THUMBNAIL.get(itemtype)
        return ItemUtil.makeThumbnailUrlMiddleByDBString(thumb)
    
    @staticmethod
    def calcUseNumMax(itemmaster, player, num):
        """一度に使用できるアイテムの最大数
        """
        if Defines.ItemEffect.USE_NUM_MAX.has_key(itemmaster.id):
            nummax = Defines.ItemEffect.USE_NUM_MAX[itemmaster.id]
        elif itemmaster.id in Defines.ItemEffect.ACTION_RECOVERY_ITEMS:
            if 0 < itemmaster.evalue:
                nummax = (player.get_ap_max() - player.get_ap() + itemmaster.evalue - 1) / itemmaster.evalue
            else:
                nummax = num
        elif itemmaster.id in Defines.ItemEffect.TENSION_RECOVERY_ITEMS:
            if 0 < itemmaster.evalue:
                nummax = (player.get_bp_max() - player.get_bp() + itemmaster.evalue - 1) / itemmaster.evalue
            else:
                nummax = num
        elif itemmaster.id == Defines.ItemEffect.CARD_BOX_EXPANSION:
            if 0 < itemmaster.evalue:
                nummax = ((Defines.CARDLIMITITEM_MAX - player.cardlimititem) + itemmaster.evalue - 1) / itemmaster.evalue
            else:
                nummax = 0
        elif itemmaster.id in Defines.ItemEffect.SCOUT_CARD_ITEMS and 0 < itemmaster.evalue:
            nummax = int((100+itemmaster.evalue - 1) / itemmaster.evalue)
        elif itemmaster.id in Defines.ItemEffect.USE_ABLE:
            nummax = num
        elif itemmaster.id == Defines.ItemEffect.CABACLUB_SCOUTMAN:
            nummax = num
        else:
            nummax = 0
        return max(0, min(nummax, num))
    
    @staticmethod
    def makeUseNumList(num):
        """一度に使用する数リスト
        """
        LENGTH = 8
        FIRST = 5
        LAST = LENGTH - FIRST
        if num <= LENGTH:
            return range(1, num+1)
        else:
            arr = range(1, FIRST+1)
            arr.extend([num - (LAST - i - 1) for i in xrange(LAST)])
        return arr
    
    NUMLIST_DEFAULT = range(1, 10) + [10, 20, 30, 40, 50, 100, 200, 400, 800, 1000]
    @staticmethod
    def makeUseNumListByList(cur_num, numlist=None):
        """一度に使用する数リスト.
        """
        numlist = numlist or ItemUtil.NUMLIST_DEFAULT[:]
        
        arr = list(numlist) + [cur_num]
        arr.sort()
        
        index = arr.index(cur_num)
        arr = arr[:index]
        
        return arr

