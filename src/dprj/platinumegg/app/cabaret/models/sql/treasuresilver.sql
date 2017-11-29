CREATE INDEX treasuresilver_uid_etime on cabaret_treasuresilver(`uid`,`etime`);
alter table `cabaret_treasuresilver` add constraint `treasuresilver_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_treasuresilver` add constraint `treasuresilver_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_treasuresilvermaster(`id`) ON DELETE CASCADE;
