alter table `cabaret_presenteveryonereceiveloginbonus` add constraint `presenteveryonereceiveloginbonus_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
