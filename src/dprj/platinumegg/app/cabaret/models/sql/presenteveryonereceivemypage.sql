alter table `cabaret_presenteveryonereceivemypage` add constraint `presenteveryonereceivemypage_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
