alter table `cabaret_battleeventbattletime` add constraint `battleeventbattletime_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventbattletime` add constraint `battleeventbattletime_oid` FOREIGN KEY (`oid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
