alter table `cabaret_battleeventscore` add constraint `battleeventscore_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventscore` add constraint `battleeventscore_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_battleeventmaster(`id`) ON DELETE CASCADE;
