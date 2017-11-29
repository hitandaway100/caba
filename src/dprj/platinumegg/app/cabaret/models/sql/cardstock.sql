alter table `cabaret_cardstock` add constraint `cardstock_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
