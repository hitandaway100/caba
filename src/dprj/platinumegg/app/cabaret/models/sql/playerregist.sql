alter table `cabaret_playerregist` add constraint `playerregist_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
