alter table `cabaret_playerexp` add constraint `playerexp_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
