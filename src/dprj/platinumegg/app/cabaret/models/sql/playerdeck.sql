alter table `cabaret_playerdeck` add constraint `playerdeck_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
