alter table `cabaret_playergold` add constraint `playergold_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
