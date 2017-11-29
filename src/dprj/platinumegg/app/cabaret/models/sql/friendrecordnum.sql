alter table `cabaret_friendrecordnum` add constraint `friendrecordnum_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
