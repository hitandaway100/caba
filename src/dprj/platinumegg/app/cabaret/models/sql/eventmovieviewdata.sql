alter table `cabaret_eventmovieviewdata` add constraint `eventmovieviewdata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_eventmovieviewdata` add constraint `eventmovieviewdata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_eventmoviemaster(`id`) ON DELETE CASCADE;
