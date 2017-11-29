alter table `cabaret_treasurebronze` add constraint `treasurebronze_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_treasurebronze` add constraint `treasurebronze_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_treasurebronzemaster(`id`) ON DELETE CASCADE;
