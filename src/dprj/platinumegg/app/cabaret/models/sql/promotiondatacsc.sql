alter table `cabaret_promotiondatacsc` add constraint `promotiondatacsc_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_promotiondatacsc` add constraint `promotiondatacsc_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_promotionprizemastercsc(`id`) ON DELETE CASCADE;
