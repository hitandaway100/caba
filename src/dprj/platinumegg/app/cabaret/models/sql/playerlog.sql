CREATE INDEX playerlog_uid_ctime on cabaret_playerlog(`uid`,`ctime`);
alter table `cabaret_playerlog` add constraint `playerlog_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
