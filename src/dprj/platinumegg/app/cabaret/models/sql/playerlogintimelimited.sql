alter table `cabaret_playerlogintimelimited` add constraint `playerlogintimelimited_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
