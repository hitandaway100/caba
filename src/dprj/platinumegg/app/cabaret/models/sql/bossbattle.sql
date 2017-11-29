alter table `cabaret_bossbattle` add constraint `bossbattle_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
