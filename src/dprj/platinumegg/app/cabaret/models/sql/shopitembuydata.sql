alter table `cabaret_shopitembuydata` add constraint `shopitembuydata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_shopitembuydata` add constraint `shopitembuydata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_shopitemmaster(`id`) ON DELETE CASCADE;
