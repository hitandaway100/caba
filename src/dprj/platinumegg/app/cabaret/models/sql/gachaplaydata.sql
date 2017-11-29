alter table `cabaret_gachaplaydata` add constraint `gachaplaydata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_gachaplaydata` add constraint `gachaplaydata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_gachaboxmaster(`id`) ON DELETE CASCADE;
