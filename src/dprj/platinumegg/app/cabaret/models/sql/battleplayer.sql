alter table `cabaret_battleplayer` add constraint `battleplayer_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
