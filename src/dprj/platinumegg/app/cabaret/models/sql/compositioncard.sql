alter table `cabaret_compositioncard` add constraint `compositioncard_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
