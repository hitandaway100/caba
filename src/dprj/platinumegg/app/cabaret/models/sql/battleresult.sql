alter table `cabaret_battleresult` add constraint `battleresult_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleresult` add constraint `battleresult_oid` FOREIGN KEY (`oid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
