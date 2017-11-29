alter table `cabaret_compositiondata` add constraint `compositiondata_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
