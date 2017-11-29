CREATE INDEX `battleeventrevenge_uid_oid` on cabaret_battleeventrevenge(`uid`,`oid`);
CREATE INDEX `battleeventrevenge_uid_ctime` on cabaret_battleeventrevenge(`uid`,`ctime`);
alter table `cabaret_battleeventrevenge` add constraint `battleeventrevenge_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_battleeventrevenge` add constraint `battleeventrevenge_oid` FOREIGN KEY (`oid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
