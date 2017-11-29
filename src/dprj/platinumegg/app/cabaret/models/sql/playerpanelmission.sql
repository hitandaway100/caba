alter table `cabaret_playerpanelmission` add constraint `playerpanelmission_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
