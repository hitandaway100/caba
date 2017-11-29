alter table `cabaret_playerap` add constraint `playerap_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
