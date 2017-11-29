alter table `cabaret_playercard` add constraint `playercard_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
