alter table `cabaret_greetplayerdata` add constraint `greetplayerdata_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
