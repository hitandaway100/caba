alter table `cabaret_battlereceivewin` add constraint `battlereceivewin_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
