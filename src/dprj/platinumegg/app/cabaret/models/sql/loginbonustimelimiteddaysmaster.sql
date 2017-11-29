alter table `cabaret_loginbonustimelimiteddaysmaster` add constraint `loginbonustimelimiteddaysmaster_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_loginbonustimelimitedmaster(`id`) ON DELETE CASCADE;
