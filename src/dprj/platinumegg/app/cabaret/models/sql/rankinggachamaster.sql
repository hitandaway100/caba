alter table `cabaret_rankinggachamaster` add constraint `rankinggachamaster_id` FOREIGN KEY (`id`) REFERENCES cabaret_gachaboxmaster(`id`) ON DELETE CASCADE;
