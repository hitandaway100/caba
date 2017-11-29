# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.models.Treasure import TreasureGold, TreasureSilver,\
    TreasureBronze, TreasureGoldMaster, TreasureSilverMaster,\
    TreasureBronzeMaster, TreasureGoldOpened, TreasureSilverOpened,\
    TreasureBronzeOpened, TreasureTableGoldMaster, TreasureTableSilverMaster,\
    TreasureTableBronzeMaster
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class TreasureSetBase:
    """宝箱.
    """
    def __init__(self, treasure, master):
        self.__treasure = treasure
        self.__master = master
    
    @property
    def id(self):
        return self.treasure.id
    @property
    def treasure(self):
        return self.__treasure
    @property
    def master(self):
        return self.__master
    
    def get_type(self):
        raise NotImplementedError
    
    @classmethod
    def get_table_cls(cls):
        raise NotImplementedError
    @classmethod
    def get_master_cls(cls):
        raise NotImplementedError
    @classmethod
    def get_model_cls(cls):
        raise NotImplementedError
    @classmethod
    def get_opened_cls(cls):
        raise NotImplementedError

class TreasureSetGold(TreasureSetBase):
    """金の宝箱.
    """
    def get_type(self):
        return Defines.TreasureType.GOLD
    
    @classmethod
    def get_table_cls(cls):
        return TreasureTableGoldMaster
    @classmethod
    def get_master_cls(cls):
        return TreasureGoldMaster
    @classmethod
    def get_model_cls(cls):
        return TreasureGold
    @classmethod
    def get_opened_cls(cls):
        return TreasureGoldOpened

class TreasureSetSilver(TreasureSetBase):
    """銀の宝箱.
    """
    def get_type(self):
        return Defines.TreasureType.SILVER
    
    @classmethod
    def get_table_cls(cls):
        return TreasureTableSilverMaster
    @classmethod
    def get_master_cls(cls):
        return TreasureSilverMaster
    @classmethod
    def get_model_cls(cls):
        return TreasureSilver
    @classmethod
    def get_opened_cls(cls):
        return TreasureSilverOpened

class TreasureSetBronze(TreasureSetBase):
    """銅の宝箱.
    """
    def get_type(self):
        return Defines.TreasureType.BRONZE
    
    @classmethod
    def get_table_cls(cls):
        return TreasureTableBronzeMaster
    @classmethod
    def get_master_cls(cls):
        return TreasureBronzeMaster
    @classmethod
    def get_model_cls(cls):
        return TreasureBronze
    @classmethod
    def get_opened_cls(cls):
        return TreasureBronzeOpened

class TreasureUtil:
    """宝箱関係いろいろ.
    """
    SET_CLASSES = {
        Defines.TreasureType.GOLD : TreasureSetGold,
        Defines.TreasureType.SILVER : TreasureSetSilver,
        Defines.TreasureType.BRONZE : TreasureSetBronze,
    }
    
    @staticmethod
    def get_modelset_cls(treasure_type):
        model_cls = TreasureUtil.SET_CLASSES.get(treasure_type)
        if model_cls is None:
            raise CabaretError(u'未実装の宝箱です')
        return model_cls
    
    @staticmethod
    def get_table_cls(treasure_type):
        """宝箱の出現テーブル.
        """
        return TreasureUtil.get_modelset_cls(treasure_type).get_table_cls()
    
    @staticmethod
    def get_master_cls(treasure_type):
        """宝箱のマスターデータのモデル.
        """
        return TreasureUtil.get_modelset_cls(treasure_type).get_master_cls()
    
    @staticmethod
    def get_model_cls(treasure_type):
        """宝箱個別情報のモデル.
        """
        return TreasureUtil.get_modelset_cls(treasure_type).get_model_cls()
    
    @staticmethod
    def get_opened_cls(treasure_type):
        """開封済み宝箱個別情報のモデル.
        """
        return TreasureUtil.get_modelset_cls(treasure_type).get_opened_cls()
    
    @staticmethod
    def createOpenedTreasure(treasure):
        """開封済みの宝箱を作成.
        """
        model_cls = treasure.__class__
        model_clsname = model_cls.__name__
        model_opened_cls = globals().get('%sOpened' % model_clsname)
        if model_opened_cls is None:
            raise CabaretError(u'開封済みテーブルが存在しません.name=%s' % model_clsname)
        
        ins = model_opened_cls()
        for field in treasure.get_fields():
            setattr(ins, field.name, getattr(treasure, field.name))
        return ins
    
    
