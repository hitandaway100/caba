alter table `cabaret_scouteventpresentnum` add constraint `scouteventpresentnum_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_scouteventpresentnum` add constraint `scouteventpresentnum_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_scouteventmaster(`id`) ON DELETE CASCADE;
