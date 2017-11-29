alter table `cabaret_scoutplaydata` add constraint `scoutplaydata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
