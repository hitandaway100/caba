alter table `cabaret_gachaplaycount` add constraint `gachaplaycount_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_gachaplaycount` add constraint `gachaplaycount_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_gachamaster(`id`) ON DELETE CASCADE;
