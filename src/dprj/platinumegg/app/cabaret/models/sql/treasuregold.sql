CREATE INDEX treasuregold_uid_etime on cabaret_treasuregold(`uid`,`etime`);
alter table `cabaret_treasuregold` add constraint `treasuregold_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_treasuregold` add constraint `treasuregold_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_treasuregoldmaster(`id`) ON DELETE CASCADE;
