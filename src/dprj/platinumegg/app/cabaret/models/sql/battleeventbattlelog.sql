CREATE INDEX `battleeventbattlelog_uid_ctime` on cabaret_battleeventbattlelog(`uid`,`ctime`);
alter table `cabaret_battleeventbattlelog` add constraint `battleeventbattlelog_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
