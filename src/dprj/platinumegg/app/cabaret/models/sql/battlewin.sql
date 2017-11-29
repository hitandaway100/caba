alter table `cabaret_battlewin` add constraint `battlewin_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
