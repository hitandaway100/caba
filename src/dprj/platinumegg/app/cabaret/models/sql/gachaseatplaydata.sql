alter table `cabaret_gachaseatplaydata` add constraint `gachaseatplaydata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_gachaseatplaydata` add constraint `gachaseatplaydata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_gachaseatmaster(`id`) ON DELETE CASCADE;
