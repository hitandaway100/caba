alter table `cabaret_scouteventplaystagedata` add constraint `scouteventplaystagedata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_scouteventplaystagedata` add constraint `scouteventplaystagedata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_scouteventstagemaster(`id`) ON DELETE CASCADE;
