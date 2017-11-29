alter table `cabaret_playerlimitation` add constraint `playerlimitation_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
