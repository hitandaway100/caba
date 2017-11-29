CREATE INDEX friendlog_uid_ctime on cabaret_friendlog(`uid`,`ctime`);
alter table `cabaret_friendlog` add constraint `friendlog_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
