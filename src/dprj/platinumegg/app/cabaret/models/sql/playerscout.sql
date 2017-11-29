alter table `cabaret_playerscout` add constraint `playerscout_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
