alter table `cabaret_raideventscore` add constraint `raideventscore_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_raideventscore` add constraint `raideventscore_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_raideventmaster(`id`) ON DELETE CASCADE;
