alter table `cabaret_playerlogin` add constraint `playerlogin_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
