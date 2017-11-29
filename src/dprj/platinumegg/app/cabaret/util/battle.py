# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.card import CardUtil
from defines import Defines
from platinumegg.app.cabaret.models.Skill import SkillMaster

class BattleUtil():
    
    @staticmethod
    def _aggregateSkillPower(playerFlag, cardset_list, skilltarget_table, rand, p_table, sp_p_table, spt_p_table, weak_p_table):
        """スキルの上昇値を集計
        """
        v_skillpowers = {}
        o_skillpowers = {}
        skillinfolist = []
        
        sp_powup_table = {}
        spt_powup_table = {}
        weak_powup_table = {}

        def get_power_up(etarget, epower, eskill, etype):
            target_power = p_table[etarget].get(etype, 0)
            if eskill:
                # Get the number of casts for a particular type (属性人数)
                cast_num = len(skilltarget_table[etarget].get(etype))
                return int(target_power * (epower / 100.0 * cast_num))
            else:
                return int(target_power * epower / 100)

        for cardset in cardset_list:
            skill = cardset.master.getSkill()
            if skill is None:
                continue
            # 発動判定.
            elif skill.get_rate(cardset.card.skilllevel) <= rand.getIntN(100):
                continue
            
            for number in xrange(SkillMaster.MULTI_SKILL_NUM_MAX):
                skilldata = skill.get_skill(number)
                if skilldata is None:
                    break
                
                if skilldata.etarget == Defines.SkillTarget.PLAYER:
                    dataset = v_skillpowers
                    epower = skilldata.epower
                    etarget = Defines.SkillTarget.PLAYER if playerFlag else Defines.SkillTarget.OPPONENT
                    eskill = skilldata.eskill
                else:
                    dataset = o_skillpowers
                    epower = -skilldata.epower
                    etarget = Defines.SkillTarget.OPPONENT if playerFlag else Defines.SkillTarget.PLAYER
                    eskill = skilldata.eskill
                
                targetlist = []
                powerUp_total = 0
                for etype in skilldata.etypelist:
                    powerUp = get_power_up(etarget, epower, eskill, etype)

                    sp_target_power = sp_p_table[etarget].get(etype, 0)
                    sp_powerUp = int(sp_target_power * epower / 100)
                    sp_powup_table[etarget] = sp_powup_table.get(etarget, 0) + sp_powerUp
                    
                    spt_target_power = spt_p_table[etarget].get(etype, 0)
                    spt_powerUp = int(spt_target_power * epower / 100)
                    spt_powup_table[etarget] = spt_powup_table.get(etarget, 0) + spt_powerUp
                    
                    weak_target_power = weak_p_table[etarget].get(etype, 0)
                    weak_powerUp = int(weak_target_power * epower / 100)
                    weak_powup_table[etarget] = weak_powup_table.get(etarget, 0) + weak_powerUp
                    
                    dataset[etype] = dataset.get(etype, 0) + powerUp
                    
                    targetlist.extend(skilltarget_table[etarget].get(etype) or [])
                    
                    powerUp_total += powerUp
                
                if targetlist:
                    targetlist = list(set(targetlist))
                    skillinfo = BattleAnimSkillInfo.create(playerFlag, skill, cardset, targetlist, powerUp_total, skilldata=skilldata)
                    skillinfolist.append(skillinfo)
        
        return v_skillpowers, o_skillpowers, skillinfolist, sp_powup_table, spt_powup_table, weak_powup_table
    
    @staticmethod
    def calcTeamPower(v_cardset_list, o_cardset_list, rand, specialcard=None, specialtype=Defines.CharacterType.ALL, specialtable=None, weakbonus=None, effect_getter=None, v_title_effect=0):
        """チームの接客力の合計を計算.
        """
        specialcard = specialcard or {}
        specialtable = specialtable or {}
        weakbonus = weakbonus or {}
        if effect_getter is None:
            effect_getter = lambda x:x
        
        specialcard_idlist = []
        
        power_table = {}
        specialcard_power_table = {}
        specialtype_power_table = {}
        weak_power_table = {}
        
        skilltarget_table = {}
        power_totals = {}
        
        for cardset_list, skilltarget, title_effect in ((v_cardset_list, Defines.SkillTarget.PLAYER, v_title_effect), (o_cardset_list, Defines.SkillTarget.OPPONENT, 0)):
            table = dict([(k, []) for k in Defines.CharacterType.SKILL_TARGET_NAMES.keys()])
            p_table = {}
            sp_p_table = {}
            spt_p_table = {}
            weak_p_table = {}
            
            power_total = 0
            
            for cardset in cardset_list:
                table[Defines.CharacterType.ALL].append(cardset.id)
                table[cardset.master.ctype].append(cardset.id)
                
                power = cardset.power
                power_total += power
                
                weak_rate = weakbonus.get(cardset.master.ctype, 100)
                
                if weak_rate != 100:
                    powerup = power * (weak_rate - 100) / 100
                    power += powerup
                    weak_p_table[Defines.CharacterType.ALL] = sp_p_table.get(Defines.CharacterType.ALL, 0) + powerup
                    weak_p_table[cardset.master.ctype] = sp_p_table.get(cardset.master.ctype, 0) + powerup
                
                if specialtype in (cardset.master.ctype, Defines.CharacterType.ALL):
                    # 属性ボーナス.
                    arr = specialtable.get(cardset.master.rare)
                    if arr and cardset.master.hklevel <= len(arr):
                        rate = arr[cardset.master.hklevel - 1]
                        powerup = power * (rate - 100) / 100
                        power += powerup
                        spt_p_table[Defines.CharacterType.ALL] = spt_p_table.get(Defines.CharacterType.ALL, 0) + powerup
                        spt_p_table[cardset.master.ctype] = spt_p_table.get(cardset.master.ctype, 0) + powerup
                
                rate = effect_getter(specialcard.get(cardset.master.id)) or 100
                if rate != 100:
                    specialcard_idlist.append(cardset.id)
                    powerup = power * (rate + title_effect - 100) / 100
                    power += powerup
                    sp_p_table[Defines.CharacterType.ALL] = sp_p_table.get(Defines.CharacterType.ALL, 0) + powerup
                    sp_p_table[cardset.master.ctype] = sp_p_table.get(cardset.master.ctype, 0) + powerup
                
                p_table[Defines.CharacterType.ALL] = p_table.get(Defines.CharacterType.ALL, 0) + power
                p_table[cardset.master.ctype] = p_table.get(cardset.master.ctype, 0) + power
            
            skilltarget_table[skilltarget] = table
            power_table[skilltarget] = p_table
            specialcard_power_table[skilltarget] = sp_p_table
            weak_power_table[skilltarget] = weak_p_table
            specialtype_power_table[skilltarget] = spt_p_table
            power_totals[skilltarget] = power_total
        
        vv_skillpowers, vo_skillpowers, v_skillinfolist, v_sp_powup_table, v_spt_powup_table, v_weak_powup_table = BattleUtil._aggregateSkillPower(True, v_cardset_list, skilltarget_table, rand, power_table, specialcard_power_table, specialtype_power_table, weak_power_table)
        oo_skillpowers, ov_skillpowers, o_skillinfolist, o_sp_powup_table, o_spt_powup_table, o_weak_powup_table = BattleUtil._aggregateSkillPower(False, o_cardset_list, skilltarget_table, rand, power_table, specialcard_power_table, specialtype_power_table, weak_power_table)
        
        def aggregate(target, cardset_list, v_skillpowers, o_skillpowers):
            power_no_skill = power_table[target].get(Defines.CharacterType.ALL, 0)
            power = power_no_skill
            for powers in (v_skillpowers, o_skillpowers):
                power += sum(powers.values())
            
            sp_power = specialcard_power_table[target].get(Defines.CharacterType.ALL, 0)
            sp_skillpowup = v_sp_powup_table.get(target, 0) + o_sp_powup_table.get(target, 0)
            
            spt_power = specialtype_power_table[target].get(Defines.CharacterType.ALL, 0)
            spt_skillpowup = v_spt_powup_table.get(target, 0) + o_spt_powup_table.get(target, 0)
            
            weak_power = weak_power_table[target].get(Defines.CharacterType.ALL, 0)
            weak_skillpowup = v_weak_powup_table.get(target, 0) + o_weak_powup_table.get(target, 0)
            
            return max(0, power), power_no_skill, sp_power + sp_skillpowup, spt_power + spt_skillpowup, weak_power + weak_skillpowup
        
        v_power, v_power_no_skill, v_sp_powup, v_spt_powup, v_weak_powup = aggregate(Defines.SkillTarget.PLAYER, v_cardset_list, vv_skillpowers, ov_skillpowers)
        o_power, o_power_no_skill, o_sp_powup, o_spt_powup, o_weak_powup = aggregate(Defines.SkillTarget.OPPONENT, o_cardset_list, oo_skillpowers, vo_skillpowers)
        
        v_power_default = power_totals[Defines.SkillTarget.PLAYER]
        o_power_default = power_totals[Defines.SkillTarget.OPPONENT]
        
        return v_power, o_power, v_power_no_skill, o_power_no_skill, v_power_default, o_power_default, v_skillinfolist, o_skillinfolist, specialcard_idlist, v_sp_powup, o_sp_powup, v_spt_powup, o_spt_powup, v_weak_powup, o_weak_powup

class BattleAnimSkillInfo:
    """スキル情報.
    """
    def __init__(self):
        self.skillUseCardId = 0
        self.playerFlag = False
        self.downFlag = False
        self.skillKind = 0
        self.skillTargetList = []
        self.skillName = None
        self.skillText = None
        self.powerUp = 0
    
    @staticmethod
    def create(playerFlag, skillmaster, skill_use_cardset, target_cardid_list, powerUp, skilldata=None):
        ins = BattleAnimSkillInfo()
        
        if skilldata and skilldata.etypelist and len(skilldata.etypelist) == 1:
            etype = skilldata.etypelist[0]
        else:
            etype = Defines.CharacterType.ALL
        
        ins.skillUseCardId = skill_use_cardset.id
        ins.playerFlag = playerFlag
        ins.downFlag = skilldata.etarget == Defines.SkillTarget.OPPONENT
        ins.skillKind = Defines.CharacterType.SKILL_TARGET_TO_EFFECT[etype]
        ins.skillTargetList = target_cardid_list[:]
        ins.skillName = skillmaster.name
        ins.skillText = skilldata.etext
        ins.powerUp = powerUp
        
        return ins

class BattleAnimParam:
    """PVPアニメーションのパラメータ.
    """
    
    def __init__(self):
        self.pSale = 0
        self.eSale = 0
        self.pCard = []
        self.eCard = []
        self.pSkill = []
        self.eSkill = []
        self.feverFlag = False
    
    @staticmethod
    def create(p_sale, e_sale, p_cardsetList, e_cardsetList, p_skillinfolist, e_skillinfolist, feverFlag):
        ins = BattleAnimParam()
        # 売上.
        ins.pSale = p_sale
        ins.eSale = e_sale
        
        # カード.
        for ins_cardlist, cardsetlist in ((ins.pCard, p_cardsetList), (ins.eCard, e_cardsetList)):
            for cardset in cardsetlist:
                ins_cardlist.append({
                    'id' : cardset.id,
                    'data':CardUtil.makeThumbnailUrlMiddle(cardset.master),
                })
        
        # スキル.
        ins.pSkill = p_skillinfolist[:]
        ins.eSkill = e_skillinfolist[:]
        
        # フィーバー.
        ins.feverFlag = feverFlag
        
        return ins
    
    def to_animation_data(self, handler):
        """演出用のパラメータにする.
        """
        data = {}
        
        # フィーバー.
        data['feverFlag'] = int(bool(self.feverFlag))
        
        # 売上.
        data['pSale'] = int(self.pSale)
        data['eSale'] = '??????'
        
        table = (
            ('p', Defines.SkillTarget.PLAYER, Defines.SkillTarget.OPPONENT),
            ('e', Defines.SkillTarget.OPPONENT, Defines.SkillTarget.PLAYER)
        )
        
        # カード.
        indexes = {
            Defines.SkillTarget.PLAYER : {},
            Defines.SkillTarget.OPPONENT : {},
        }
        for prefix, skilltarget, _ in table:
            attname = '%sCard' % prefix
            cardlist = getattr(self, attname)
            
            indextable = Defines.EffectIndexTables.BATTLE.get(len(cardlist)) or range(1, len(cardlist)+1)
            
            for i, carddata in enumerate(cardlist):
                index = indextable[i]
                data['%s%d' % (attname, index)] = handler.makeAppLinkUrlImg(carddata['data'])
                indexes[skilltarget][carddata['id']] = index
        
        def cardidToIndex(skilltarget, cardid):
            return indexes[skilltarget][cardid]
        
        # スキル.
        for prefix, v_skilltarget, o_skilltarget in table:
            
            skilllist = getattr(self, '%sSkill' % prefix)
            skillcount = len(skilllist)
            
            data['%sSkillCount' % prefix] = skillcount
            
            if skillcount < 1:
                continue
            
            skillUseChara = []
            playerFlag = []
            downFlag  = []
            skillKind = []
            skillNum = []
            skillIndex = []
            skillName = []
            skillText = []
            skillValue = []
            
            for skillinfo in skilllist:
                skillUseChara.append(str(cardidToIndex(v_skilltarget, skillinfo.skillUseCardId)))
                downFlag.append(str(int(bool(skillinfo.downFlag))))
                skillKind.append(str(skillinfo.skillKind))
                
                skillNum.append(str(len(skillinfo.skillTargetList)))
                
                if skillinfo.downFlag:
                    skilltarget = o_skilltarget
                else:
                    skilltarget = v_skilltarget
                
                if skilltarget == Defines.SkillTarget.PLAYER:
                    playerFlag.append('1')
                else:
                    playerFlag.append('0')
                
                skillIndex.append(','.join([str(cardidToIndex(skilltarget, targetcardid)) for targetcardid in skillinfo.skillTargetList]))
                skillName.append(skillinfo.skillName.replace(':', '__COLON__'))
                skillText.append(skillinfo.skillText.replace(':', '__COLON__'))
                if skillinfo.powerUp < 0:
                    skillValue.append(str(-skillinfo.powerUp))
                else:
                    skillValue.append(str(skillinfo.powerUp))
            
            data['%sSkillUseChara' % prefix] = ':'.join(skillUseChara)
            data['%sPlayerFlag' % prefix] = ':'.join(playerFlag)
            data['%sDownFlag' % prefix] = ':'.join(downFlag)
            data['%sSkillKind' % prefix] = ':'.join(skillKind)
            data['%sSkillNum' % prefix] = ':'.join(skillNum)
            data['%sSkillIndex' % prefix] = ':'.join(skillIndex)
            data['%sSkillName' % prefix] = ':'.join(skillName)
            data['%sSkillText' % prefix] = ':'.join(skillText)
            data['%sSkillValue' % prefix] = ':'.join(skillValue)
        
        return data
    
    def make_html_skilllist(self, is_player):
        """HTML埋め込み用のスキル.
        """
        if is_player:
            arr = self.pSkill
        else:
            arr = self.eSkill
        
        response = []
        exists = []
        for skillinfo in arr:
            if skillinfo.skillUseCardId in exists:
                continue
            exists.append(skillinfo.skillUseCardId)
            response.append({
                'color' : Defines.CharacterType.Effect.TEXT_COLOR.get(skillinfo.skillKind),
                'name' : skillinfo.skillName,
            })
        return response

class BossBattleAnimParam():
    """ボス戦演出パラメータ.
    """
    
    def __init__(self):
        self.winFlag = False
        self.power = 0
        self.power_default = 0
        self.leader = None
        self.memberlist = []
        self.skilllist = []
        self.bossHpPre = 0
        self.bossHpPost = 0
        self.bossHpMax = 0
        self.bossDamage = 0
        self.critical = False
        self.specialcard_idlist = None
        self.specialcard_powup = None
        self.weak_powup = None
    
    @staticmethod
    def create(power, power_default, cardlist, skilllist, damage, hppre, hppost, hpmax, critical, specialcard_idlist=None, friendcard=None, sppowup=None, weakpowup=None):
        ins = BossBattleAnimParam()
        
        # 勝利フラグ.
        ins.winFlag = hppost < 1
        
        # 接客力とか.
        ins.power = power
        ins.power_default = power_default
        ins.specialcard_powup = sppowup
        ins.weak_powup = weakpowup
        
        # ボス.
        ins.bossHpPre = hppre
        ins.bossHpPost = hppost
        ins.bossHpMax = hpmax
        ins.bossDamage = damage
        
        # カード.
        leader = cardlist[0]
        ins.leader = {
            'id' : leader.id,
            'data':CardUtil.makeThumbnailUrlMiddle(leader.master),
        }
        for cardset in cardlist[1:]:
            ins.memberlist.append({
                'id' : cardset.id,
                'data':CardUtil.makeThumbnailUrlIcon(cardset.master),
            })
        if friendcard:
            ins.memberlist.append({
                'id' : friendcard.id,
                'data':CardUtil.makeThumbnailUrlIcon(friendcard.master),
                'friend' : True,
            })
        
        # スキル.
        ins.skilllist = skilllist[:]
        
        ins.specialcard_idlist = specialcard_idlist or []
        
        return ins
    
    def to_animation_data(self, handler):
        """演出用のパラメータにする.
        """
        data = {}
        
        # 勝利フラグ.
        data['winFlag'] = int(bool(self.winFlag))

        # ボス.
        gauge_pre = int((self.bossHpMax - self.bossHpPre) * 100 / self.bossHpMax)
        gauge_post = int((self.bossHpMax - self.bossHpPost) * 100 / self.bossHpMax)
        
        data['bossGauge'] = '%d:%d' % (gauge_pre, gauge_post)
        data['bossDamage'] = self.bossDamage
        
        # カード.
        activePlayer = []
        indexes = {}
        cardlist = [self.leader] + self.memberlist
        index = 1
        for carddata in cardlist:
            if carddata.get('friend'):
                continue
            data['image%d' % index] = handler.makeAppLinkUrlImg(carddata['data'])
            indexes[carddata['id']] = index
            activePlayer.append(str(index))
            index += 1
        
        data['activePlayer'] = ':'.join(activePlayer)
        data['playerMax'] = len(activePlayer)
        
        helpPlayer = []
        for cardid in self.specialcard_idlist:
            if not indexes.has_key(cardid):
                continue
            index = indexes[cardid]
            helpPlayer.append(str(index))
        
        data['helpFlag'] = str(int(0 < len(helpPlayer)))
        data['helpPlayer'] = ':'.join(helpPlayer)
        
        return data
    
    def make_html_skilllist(self):
        """HTML埋め込み用のスキル.
        """
        response = []
        exists = []
        for skillinfo in self.skilllist:
            if skillinfo.skillUseCardId in exists:
                continue
            exists.append(skillinfo.skillUseCardId)
            response.append({
                'color' : Defines.CharacterType.Effect.TEXT_COLOR.get(skillinfo.skillKind),
                'name' : skillinfo.skillName,
            })
        return response


