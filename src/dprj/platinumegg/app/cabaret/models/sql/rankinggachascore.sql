alter table `cabaret_rankinggachascore` add constraint `rankinggachascore_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_rankinggachascore` add constraint `rankinggachascore_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_rankinggachamaster(`id`) ON DELETE CASCADE;
