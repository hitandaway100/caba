alter table `cabaret_albumacquisition` add constraint `albumacquisition_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
