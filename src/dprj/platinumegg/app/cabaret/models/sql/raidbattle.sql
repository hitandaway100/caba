alter table `cabaret_raidbattle` add constraint `raidbattle_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
