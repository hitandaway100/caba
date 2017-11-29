alter table `cabaret_raiddeck` add constraint `raiddeck_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
