alter table `cabaret_battlelose` add constraint `battlelose_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
