# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import datetime
from platinumegg.app.cabaret.models.UserLog import UserLogLoginBonus,\
    UserLogCardGet, UserLogCardSell, UserLogComposition, UserLogEvolution,\
    UserLogGacha, UserLogAreaComplete, UserLogScoutComplete, UserLogPresentSend,\
    UserLogPresentReceive, UserLogItemGet, UserLogItemUse, UserLogTreasureGet,\
    UserLogTreasureOpen, UserLogTrade, UserLogTicketGet,\
    UserLogLoginBonusTimeLimited, UserLogComeBack, UserLogCardStock,\
    UserLogLoginbonusSugoroku, UserLogCabaClubStore, UserLogReprintTicketTradeShop
from platinumegg.app.cabaret.models.Card import CardDeleted
from platinumegg.app.cabaret.models.Present import PresentReceived
from platinumegg.app.cabaret.models.Treasure import TreasureGoldOpened,\
    TreasureSilverOpened, TreasureBronzeOpened
from platinumegg.app.cabaret.models.Happening import Happening, Raid, RaidLog,\
    RaidHelp
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventSpecialBonusScoreLog,\
    RaidEventHelpSpecialBonusScore
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerDataWeekly
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

class Command(BaseCommand):
    """パーティション作成用のSQLを作成.
    """
    BASE_QUERYSTRING = {
        'create':"ALTER TABLE `%s` PARTITION BY RANGE(%s)(PARTITION `%s` VALUES LESS THAN (%s));",
        'add':"ALTER TABLE `%s` ADD PARTITION (PARTITION `%s` VALUES LESS THAN (%s));\n",
        'drop':"ALTER TABLE `%s` DROP PARTITION `%s`;\n",
    }
    TARGET_TABLE = (
        (UserLogLoginBonus, 'ctime', '', None),
        (UserLogCardGet, 'ctime', '', None),
        (UserLogCardSell, 'ctime', '', None),
        (UserLogComposition, 'ctime', '', None),
        (UserLogEvolution, 'ctime', '', None),
        (UserLogGacha, 'ctime', '', None),
        (UserLogAreaComplete, 'ctime', '', None),
        (UserLogScoutComplete, 'ctime', '', None),
        (UserLogPresentSend, 'ctime', '', None),
        (UserLogPresentReceive, 'ctime', '', None),
        (UserLogItemGet, 'ctime', '', None),
        (UserLogItemUse, 'ctime', '', None),
        (UserLogTreasureGet, 'ctime', '', None),
        (UserLogTreasureOpen, 'ctime', '', None),
        (UserLogTrade, 'ctime', '', None),
        (UserLogReprintTicketTradeShop, 'ctime', '', None),
        (UserLogTicketGet, 'ctime', '', None),
        (UserLogLoginBonusTimeLimited, 'ctime', '', None),
        (UserLogComeBack, 'ctime', '', None),
        (UserLogCardStock, 'ctime', '', None),
        (UserLogLoginbonusSugoroku, 'ctime', '', None),
        (UserLogCabaClubStore, 'ctime', '', None),
        (CardDeleted, 'dtime', '', None),
        (PresentReceived, 'ctime', '', None),
        (TreasureGoldOpened, 'otime', '', None),
        (TreasureSilverOpened, 'otime', '', None),
        (TreasureBronzeOpened, 'otime', '', None),
        (Happening, 'ctime', '', None),
        (Raid, 'ctime', '', None),
        (RaidLog, 'ctime', '', None),
        (RaidHelp, 'ctime', '', None),
        (RaidEventSpecialBonusScoreLog, 'ctime', '', None),
        (RaidEventHelpSpecialBonusScore, 'ctime', '', None),
        (CabaClubScorePlayerDataWeekly, 'week', '', 'week')
    )
    
    class IndispensableArgs:
        NUM_MAX = 3
        (
            PROCESS,
            TARGET_DATE,
            OUTPUT,
        ) = range(NUM_MAX)
    
    def handle(self, *args, **options):
        
        proc = args[Command.IndispensableArgs.PROCESS]
        str_target_date = args[Command.IndispensableArgs.TARGET_DATE]
        
        tmp_date = datetime.datetime.strptime(str_target_date, "%Y%m") + datetime.timedelta(days=31)
        target_date = datetime.datetime(tmp_date.year, tmp_date.month, 1)
        
        table = {
            'create':self.make_create_sql,
            'add':self.make_add_sql,
            'drop':self.make_drop_sql,
        }
        func = table.get(proc)
        if func is None:
            print "Not Found:process '%s'" % proc
            return
        
        for target in Command.TARGET_TABLE:
            model_cls, column_name, partition_head, datetime_to_sql_name = target
            if datetime_to_sql_name is None:
                field = model_cls.get_field(column_name)
                datetime_to_sql_name = field.get_internal_type().lower()
            datetime_to_sql = getattr(self, 'datetime_to_sql_%s' % (datetime_to_sql_name))
            querystring = func(partition_head, target_date, model_cls, column_name, datetime_to_sql)
            print querystring
    
    def make_partition_name(self, head, target_date):
        """パーティションの名前を作成.
        """
        return '%s%s' % (head, target_date.strftime("%Y%m01"))
    
    def make_create_sql(self, partition_head, target_date, model_cls, column_name, datetime_to_sql):
        """作成用sql作成.
        """
        table_name = model_cls.get_tablename()
        partition_name = self.make_partition_name(partition_head, target_date)
        return Command.BASE_QUERYSTRING['create'] % (table_name, datetime_to_sql('`%s`' % column_name), partition_name, datetime_to_sql(target_date))
        
    def make_add_sql(self, partition_head, target_date, model_cls, column_name, datetime_to_sql):
        """追加用sql作成.
        """
        table_name = model_cls.get_tablename()
        partition_name = self.make_partition_name(partition_head, target_date)
        return Command.BASE_QUERYSTRING['add'] % (table_name, partition_name, datetime_to_sql(target_date))
        
    def make_drop_sql(self, partition_head, target_date, model_cls, column_name, datetime_to_sql):
        """削除用sql作成.
        """
        table_name = model_cls.get_tablename()
        partition_name = self.make_partition_name(partition_head, target_date)
        return Command.BASE_QUERYSTRING['drop'] % (table_name, partition_name)
    
    #=====================================================================================
    def datetime_to_sql_datetimefield(self, dt):
        """DateTime型のカラムのパーティション用のSQLに変換.
        """
        if isinstance(dt, datetime.datetime):
            dt = dt.strftime('"%Y-%m-01 00:00:00"')
        return 'TO_DAYS(%s)' % dt
    
    def datetime_to_sql_week(self, dt):
        """週間データのカラムのパーティション用のSQLに変換.
        """
        if isinstance(dt, datetime.datetime):
            dt = DateTimeUtil.strToDateTime(dt.strftime("%Y-%m-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
            endtime = BackendApi.to_cabaretclub_section_endtime(dt)
            v = endtime.strftime("%Y%W")
        else:
            v = dt
        return v

