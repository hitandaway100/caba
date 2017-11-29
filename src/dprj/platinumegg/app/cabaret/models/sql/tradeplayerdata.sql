alter table `cabaret_tradeplayerdata` add constraint `tradeplayerdata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_tradeplayerdata` add constraint `tradeplayerdata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_trademaster(`id`) ON DELETE CASCADE;
