alter table `cabaret_battleeventpresentcounts` add constraint `battleeventpresentcounts_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
