CREATE INDEX friend_uid_state on cabaret_friend(`uid`,`state`);
alter table `cabaret_friend` add constraint `friend_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_friend` add constraint `friend_fid` FOREIGN KEY (`fid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
