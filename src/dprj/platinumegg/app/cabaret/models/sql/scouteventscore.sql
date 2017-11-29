alter table `cabaret_scouteventscore` add constraint `scouteventscore_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_scouteventscore` add constraint `scouteventscore_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_scouteventmaster(`id`) ON DELETE CASCADE;
