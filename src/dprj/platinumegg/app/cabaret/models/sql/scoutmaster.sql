alter table `cabaret_scoutmaster` add constraint `scoutmaster_area` FOREIGN KEY (`area`) REFERENCES cabaret_areamaster(`id`) ON DELETE CASCADE;
