alter table `cabaret_battleeventpresentdata` add constraint `battleeventpresentdata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventpresentdata` add constraint `battleeventpresentdata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
