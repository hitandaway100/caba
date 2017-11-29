alter table `cabaret_raiddestroycount` add constraint `raiddestroycount_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
