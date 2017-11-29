alter table `cabaret_item` add constraint `item_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_item` add constraint `item_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_itemmaster(`id`) ON DELETE CASCADE;
