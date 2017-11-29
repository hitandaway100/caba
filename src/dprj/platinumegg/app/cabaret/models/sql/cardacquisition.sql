alter table `cabaret_cardacquisition` add constraint `cardacquisition_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
