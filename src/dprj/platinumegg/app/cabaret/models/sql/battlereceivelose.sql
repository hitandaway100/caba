alter table `cabaret_battlereceivelose` add constraint `battlereceivelose_id` FOREIGN KEY (`id`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
