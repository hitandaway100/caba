alter table `cabaret_invitedata` add constraint `invitedata_fid` FOREIGN KEY (`fid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
