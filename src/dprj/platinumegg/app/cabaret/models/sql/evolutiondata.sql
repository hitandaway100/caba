alter table `cabaret_evolutiondata` add constraint `evolutiondata_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
