CREATE INDEX revenge_uid_ctime on cabaret_revenge(`uid`,`ctime`);
alter table `cabaret_revenge` add constraint `revenge_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_revenge` add constraint `revenge_oid` FOREIGN KEY (`oid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
