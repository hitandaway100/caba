alter table `cabaret_greetdata` add constraint `greetdata_fromid` FOREIGN KEY (`fromid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_greetdata` add constraint `greetdata_toid` FOREIGN KEY (`toid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
