alter table `cabaret_scouteventplaydata` add constraint `scouteventplaydata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_scouteventplaydata` add constraint `scouteventplaydata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_scouteventmaster(`id`) ON DELETE CASCADE;
