# -*- coding: utf-8 -*-

from platinumegg.app.cabaret.models.base import *

# ここでモデルをインポートしとかないと Sync DB したときにテーブルが作成されない.
from platinumegg.app.cabaret.models.Player import *
from platinumegg.app.cabaret.models.Card import *
from platinumegg.app.cabaret.models.Item import *
from platinumegg.app.cabaret.models.Boss import *
from platinumegg.app.cabaret.models.Area import *
from platinumegg.app.cabaret.models.Scout import *
from platinumegg.app.cabaret.models.Happening import *
from platinumegg.app.cabaret.models.Battle import *
from platinumegg.app.cabaret.models.Skill import *
from platinumegg.app.cabaret.models.Greet import *
from platinumegg.app.cabaret.models.Infomation import *
from platinumegg.app.cabaret.models.AccessBonus import *
from platinumegg.app.cabaret.models.Present import *
from platinumegg.app.cabaret.models.PlayerLog import *
from platinumegg.app.cabaret.models.Friend import *
from platinumegg.app.cabaret.models.Memories import *
from platinumegg.app.cabaret.models.Gacha import *
from platinumegg.app.cabaret.models.Shop import *
from platinumegg.app.cabaret.models.AppConfig import *
from platinumegg.app.cabaret.models.Text import *
from platinumegg.app.cabaret.models.PresentEveryone import *
from platinumegg.app.cabaret.models.Schedule import *
from platinumegg.app.cabaret.models.PlayerLevelExp import *
from platinumegg.app.cabaret.models.CardLevelExp import *
from platinumegg.app.cabaret.models.PaymentEntry import *
from platinumegg.app.cabaret.models.Tutorial import *
from platinumegg.app.cabaret.models.Treasure import *
from platinumegg.app.cabaret.models.Trade import *
from platinumegg.app.cabaret.models.TradeShop import *
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import *
from platinumegg.app.cabaret.models.UserLog import *
from platinumegg.app.cabaret.models.Invite import *
from platinumegg.app.cabaret.models.SerialCampaign import *
from platinumegg.app.cabaret.models.promotion.koihime import *
from platinumegg.app.cabaret.models.promotion.csc import *
from platinumegg.app.cabaret.models.ComeBack import *
from platinumegg.app.cabaret.models.Mission import *
from platinumegg.app.cabaret.models.LevelUpBonus import *
from platinumegg.app.cabaret.models.CabaretClub import *
from platinumegg.app.cabaret.models.Title import *
from platinumegg.app.cabaret.models.GachaExplain import *

# Event.
from platinumegg.app.cabaret.models.Scenario import *
from platinumegg.app.cabaret.models.raidevent.RaidEvent import *
from platinumegg.app.cabaret.models.raidevent.RaidCardMixer import *
from platinumegg.app.cabaret.models.raidevent.RaidEventScout import *
from platinumegg.app.cabaret.models.ScoutEvent import *
from platinumegg.app.cabaret.models.battleevent.BattleEvent import *
from platinumegg.app.cabaret.models.battleevent.BattleEventPresent import *
from platinumegg.app.cabaret.models.CabaretClubEvent import *
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import *

#NgCast
from platinumegg.app.cabaret.models.NgCast import *
