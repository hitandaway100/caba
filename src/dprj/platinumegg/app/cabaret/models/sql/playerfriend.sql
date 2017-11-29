alter table `cabaret_playerfriend` add constraint `playerfriend_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
