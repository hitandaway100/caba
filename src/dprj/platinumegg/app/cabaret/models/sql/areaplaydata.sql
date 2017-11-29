alter table `cabaret_areaplaydata` add constraint `areaplaydata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
