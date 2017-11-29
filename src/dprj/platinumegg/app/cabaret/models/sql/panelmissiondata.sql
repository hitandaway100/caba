alter table `cabaret_panelmissiondata` add constraint `panelmissiondata_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_panelmissiondata` add constraint `panelmissiondata_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_panelmissionpanelmaster(`id`) ON DELETE CASCADE;
