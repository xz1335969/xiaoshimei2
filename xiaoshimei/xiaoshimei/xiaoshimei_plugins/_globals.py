import random

TYPELIST = {
    "weapon": 0,
    "shield": 1,
    "item": 2,
    "offhand": 3,
}

EXTRA_MODULES = [
    'group_id',  # 0
    'setujinyan',  # 1
    'help',  # 2
    'ipackage',  # 3
    'legend_box',  # 4
    'fusion',  # 5
    'sell',  # 6
    'drillshop',  # 7
    'chaoshen',  # 9
    'strength',  # 11
    'monijinglian',  # 12
    'signin',  # 13
    'gold_query',  # 14
    'gold_present',  # 15
    'gold_shop',  # 16
    'rob',  # 17
    'gamble',  # 18
    'guess_coin',  # 19
    'wawale',  # 20
    'heisi',  # 21
    'leavemsg',  # 22
    'leave_private_msg',  # 23
    'left_msg',  # 24
    'left_msg_all',  # 25
    'sleep_time',  # 29
    'sleep_list',  # 30
    'group_release_all',  # 31
    'blessing',

]

EXTRA_MODULES2 = [
    '涩图禁言',  # 1
    '仓库',  # 3
    '神器盒子',  # 4
    '模拟熔炼',  # 5
    '出售物品',  # 6
    '钻头商城',  # 7
    '弹王兑换',  # 8 9 10
    '模拟强化',  # 11
    '模拟精炼',  # 12
    '签到',  # 13 14 15 16
    '抢劫',  # 17
    '金币小游戏',  # 18 19 20
    '留言',  # 22 23 24 25
    '小师妹交流',  # 26 27 28 21
    '睡眠套餐',  # 29 30 31

]

image_reply = {
    'weapon': {"武器", "武器属性", "武器介绍"},
    'delay': {"d值", "d值计算"},
    'jiashen': {"假神", "假神任务", "假神获取"},
    'jiezhi': {"戒指", "戒指属性"},
    'shouzhuo': {"手镯", "手镯属性"},
    'petskill': {"宠物技能", },
    # 'petgrow': {"宠物属性", "宠物成长"},
    'kaikong': {"开孔", "开孔需求"},
    'xiulian': {"修炼", "修炼属性", "修炼需求"},
    'cardstatus': {"卡牌属性", "卡牌介绍"},
    'lidubiao': {'力度表', '65度打法', '20度打法', '30度打法', '50度打法'},
    'ronglian': {"强化活动", "强化熔炼活动"},
    'PVE_info': {"副本攻略", },
    'level_and_exp': {"升级经验", },
    'kaji': {"卡级", "卡级说明"},
    'jinglian': {"精炼"}
}
text_reply = {
    'shoushi': [{"首饰", "首饰属性", "首饰介绍"}, '请选择你要查询的首饰类型：\n 戒指 \n 手镯'],
    'pet': [{"宠物", "宠物介绍"}, "请选择要查询的类型：\n 宠物技能 \n 宠物成长"],
    'card': [{"卡牌", }, "请选择要查询的类型：\n  卡牌属性 \n  做卡推荐"],
    'cardrecommand': [{"做卡推荐", }, """萌新推荐做卡：
任何一种卡升到10级大约需要180盒，升到20级大约需要700盒，升到升到30级大约需要1850盒,加上初步洗点大概需要2000盒。所以商人出售的秒30卡一般指1998盒两组。根据自己的需求来选择做卡。

1.白嫖党：当然不做了，慢慢挂本白嫖就行了。
2.微氪党：魔狼卡/魔鹰卡二选一做一套+其他任意三张二属性卡，主卡一张1级牛头人卡
3.小氪党：任意二属性两套(推荐选运动会2属性)+小恶魔卡+拳王卡，主卡一张1级牛头人卡
4.中氪党：魔狼卡/魔鹰卡二选一做一套+小恶魔卡+拳王卡+任意二属性卡+酋长/裁判/国王/里格理主卡
5.重氪党：上面的基础上二属性卡换成哥布林战士 和 道拉夫上校卡
6.大老板：四神或者五神"""],
}

EXTRA_MODULES3 = [[1], [3], [4], [5], [6], [7], [8, 9, 10], [11], [12], [13, 14, 15, 16], [17], [18, 19, 20],
                  [22, 23, 24, 25], [28, 27, 28, 21], [29, 30, 31]]


def randomlist(list1: list):
    for i in range(len(list1) - 1):
        num = random.randint(i, len(list1) - 1)
        _ = list1[num]
        list1[num] = list1[i]
        list1[i] = _
    return list1


def overrandom(items: list[tuple] | dict):
    if type(items) == list:
        keys = [i[0] for i in items]
        rates = [i[1] for i in items]
    else:
        keys = [i for i in items]
        rates = [items[i] for i in keys]
    rate_all = sum(rates)
    rand = random.randint(1, rate_all)
    i = 0
    for j in range(len(keys)):
        rand -= rates[j]
        if rand <= 0:
            i = int(j)
            break
    return keys[i]
