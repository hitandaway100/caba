alter table `cabaret_scouteventflags` add constraint `scouteventflags_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_scouteventflags` add constraint `scouteventflags_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_scouteventmaster(`id`) ON DELETE CASCADE;
