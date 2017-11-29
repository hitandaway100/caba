alter table `cabaret_playergachapt` add constraint `playergachapt_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
