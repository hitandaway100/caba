alter table `cabaret_invite` add constraint `invite_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_invite` add constraint `invite_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_invitemaster(`id`) ON DELETE CASCADE;
