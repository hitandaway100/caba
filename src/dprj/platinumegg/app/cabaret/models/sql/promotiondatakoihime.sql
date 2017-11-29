alter table `cabaret_promotiondatakoihime` add constraint `promotiondatakoihime_uid` FOREIGN KEY (`uid`) REFERENCES cabaret_player(`id`) ON DELETE CASCADE;
alter table `cabaret_promotiondatakoihime` add constraint `promotiondatakoihime_mid` FOREIGN KEY (`mid`) REFERENCES cabaret_promotionprizemasterkoihime(`id`) ON DELETE CASCADE;
