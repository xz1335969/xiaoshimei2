from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *
from . import createImage,superuser,legendbox,scheduler,simulate_fusion,extra


signin = on_command("signin", aliases={"每日签到", '签到'})
gold_query = on_command("gold_query", aliases={"查询金币", "查金币"})
gold_recharge = on_command("gold_recharge", aliases={"充值金币", })
gold_present = on_command("gold_present", aliases={"赠送金币", })
gold_shop = on_command("gold_shop", aliases={"金币商店", "金币商城"})
user_package = on_command("package", aliases={"查看仓库", "查询仓库", "查看背包"})


@signin.handle()
async def _(event: GroupMessageEvent, matcher: Matcher):
    player = Person(event.user_id, event.group_id)
    auth = authority(event.group_id, "signin")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await matcher.finish("请在1:00——10:00期间使用本系统")
    report = player.signin()
    await signin.finish(report)


@gold_query.handle()
async def _(event: GroupMessageEvent, matcher: Matcher, arg: Message = CommandArg()):
    auth = authority(event.group_id, "gold_query")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await matcher.finish("请在1:00——10:00期间使用本系统")
    arg = arg.extract_plain_text().strip()
    qid = get_qq(arg) if arg else event.user_id
    player = Person(qid, event.group_id)
    result = player.gold if player.gold else 0
    await gold_query.finish(MessageSegment.at(qid) + f"的金币数量为{result}")


@gold_recharge.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    player = Person(event.user_id, event.group_id)
    if not player.is_superuser:
        await gold_recharge.finish("您的权限不足")
        return
    else:
        args = arg.extract_plain_text().strip().split()
        num = int(args[0])
        if len(args) == 0:
            player.gold += num
            player.refresh()
            await gold_recharge.finish('为' + MessageSegment.at(player.user_id) + f'充值{num}金币成功')
            return
        else:
            players = ""
            for i, cq in enumerate(args):
                if i == 0:
                    continue
                else:
                    qq_num = get_qq(cq)
                    player = Person(qq_num, event.group_id)
                    player.gold += num
                    player.refresh()
                    players = players + MessageSegment.at(player.player_id)
    await gold_recharge.finish(f'为{players}充值{num}金币成功')


@gold_present.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    user_id = event.user_id
    group_id = event.group_id
    auth = authority(event.group_id, "gold_query")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await gold_present.finish("请在1:00——10:00期间使用本系统")
    args = arg.extract_plain_text().split()
    to_qq_num = get_qq(args[1])
    num = int(args[0])
    num = (-1 * num) if num < 0 else num
    from_person = Person(user_id, group_id)
    to_person = Person(to_qq_num, group_id)
    if from_person.gold < num:
        await gold_present.finish("您的金币不足")
    else:
        from_person.gold -= num
        from_person.refresh()
        to_person.gold += num
        to_person.refresh()
        await gold_present.finish("赠送成功")


async def get_buy_num(event: GroupMessageEvent, state: T_State):
    arg = str(state["player_buy_num"])
    item_to_buy = state["item_to_buy"]
    player = state["player"]
    rest = state["rest"]
    player_buy_num = int(arg.strip())
    if player_buy_num <= 0:
        await gold_shop.finish("请输入正确的数字")
    elif rest and player_buy_num > rest:
        await gold_shop.finish("购买数量超过上限！")
    elif player.gold < player_buy_num * item_to_buy.price:
        await gold_shop.finish("您的金币不足")
    return {**state, "player_buy_num": player_buy_num}


@gold_shop.handle()
async def _(event: GroupMessageEvent, state: T_State):
    user_id = event.user_id
    group_id = event.group_id
    auth = authority(event.group_id, "gold_shop")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await gold_present.finish("请在1:00——10:00期间使用本系统")
    player = Person(user_id, group_id)
    shop = Shop(player)
    state["player"] = player
    state["shop"] = shop
    state["prompt"] = shop.showlist()


@gold_shop.got("player_choice", prompt=MessageTemplate("{prompt}"))
async def _(event: GroupMessageEvent, matcher: Matcher, state: T_State):
    shop = state["shop"]
    arg = str(state["player_choice"]).strip().split(" ")
    try:
        player_choice_shop_id = int(arg[0])
    except ValueError:
        await gold_shop.finish("购买出错，请输入正确的编号数字")
    except IndexError:
        await gold_shop.finish("请输入内容")
    else:
        if player_choice_shop_id not in shop.shop_id_list:
            await gold_shop.finish("购买出错，请输入正确的编号数字")
        else:
            item_to_buy = shop.goods_list[shop.shop_id_list.index(player_choice_shop_id)]
            limit_type_txt = ['', "", "本月", "今日"]
            lmt_txt = limit_type_txt[item_to_buy.limit_type]
            if player_choice_shop_id not in shop.show_list:
                await gold_shop.finish(f"该物品购买数量已经达到{lmt_txt}上限")
            else:
                rest = item_to_buy.shop_limit - item_to_buy.bought_times
                state["rest"] = rest
                state["item_to_buy"] = item_to_buy
                state["player_choice_shop_id"] = player_choice_shop_id
                if len(arg) > 1:
                    state["player_buy_num"] = int(arg[1])
                else:
                    __ = f"({lmt_txt})剩余{rest}" if item_to_buy.limit_type > 0 else ""
                    state["prompt"] = "请输入购买数量：" + __


@gold_shop.got("player_buy_num", prompt=MessageTemplate("{prompt}"))
async def _(event: GroupMessageEvent, state: T_State = Depends(get_buy_num)):
    player_buy_num = int(state["player_buy_num"])
    item_to_buy = state["item_to_buy"]
    player = state["player"]
    rest = state["rest"]
    player_choice_shop_id = state["player_choice_shop_id"]
    if player_buy_num <= 0:
        await gold_shop.finish("请输入正确的数字")
    elif rest and player_buy_num > rest:
        await gold_shop.finish("购买数量超过上限！")
    elif player.gold < player_buy_num * item_to_buy.price:
        await gold_shop.finish("您的金币不足")
    player.query()
    player.gold -= player_buy_num * item_to_buy.price
    item_to_buy.count *= player_buy_num
    if item_to_buy.item_id in player.package.keys():
        player.package[item_to_buy.item_id].count += item_to_buy.count
    else:
        player.package[item_to_buy.item_id] = item_to_buy
    player.refresh_all()
    if item_to_buy.limit_type > 0:
        sqlquery(INSERT, "shop_limit", None,
                 ("shop_id", "player_id", "count"),
                 (player_choice_shop_id, player.player_id, player_buy_num)
                 )
    await gold_shop.finish("购买成功")


@user_package.handle()
async def _(event: GroupMessageEvent):
    user_id = event.user_id
    group_id = event.group_id
    auth = authority(event.group_id, "ipackage")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await gold_present.finish("请在1:00——10:00期间使用本系统")
    player = Person(user_id, group_id)
    player.query()
    result = player.print_package()
    report = MessageSegment.at(user_id) + "的仓库如下" + MessageSegment.image(
        f"file:///{__file__.strip('__init__.py')}../temp/temp_bag.png") if result else MessageSegment.at(
        user_id) + "的仓库为空"
    await user_package.finish(report)





# mine_sweep = on_command("mine_sweep",aliases={"扫雷游戏","挖挖乐2"})
#
#
# class MineSweepGame:
#     def __init__(self,gold,mine = 50):
#         self._GAME_OVER = 1
#         self._GET_GOLD = 2
#         self._GET_ITEM = 3
#         self.initgold = gold
#         mine_map = [0]*100
#         i = 0
#         while sum(mine_map)<= mine - 2:
#             mine_map[i] += random.randint(1,3)
#             i += 1
#         while sum(mine_map)<= mine:
#             mine_map[i] += random.randint(1,50-sum(mine_map))
#             i += 1
#         for j in range(i,i+5):
#             mine_map[j] = "item"
#         i += 10
#         for j in range(i,i+20):
#             mine_map[j] = "gold"
#         j += 1
#         while j < 100:
#             mine_map[j] = "empty"
#             j += 1
#         randomlist(mine_map)
#         self.mine_map = mine_map
#         self.gold = 0
#
#
#     def __str__(self):
#         return """扫雷游戏，挖挖乐的升级版、
#         扫雷说明：10*10的块中一共有50个雷，5个物品格子和20个金币格子。每个格子最多有三个雷，所在格子的数字代表周围8格雷的数量之和，请尝试找出全部的雷吧。踩到地雷游戏结束，你可以随时发送“取消”来结束游戏，获得你的所有物品的一半"""
#
#
#     def sweep(self,block:int):
#         """
#         点击地址
#         :param block: 挖某个格子
#         :return:结果
#         """
#         chosen_block = self.mine_map[block]
#         if type(chosen_block) == int and chosen_block > 0:
#             self.game_over()
#             return self._GAME_OVER
#         elif chosen_block == "empty":
#             chosen_block = 0
#             return 0
#         elif chosen_block == "gold":
#             self.gold += int(self.initgold * random.uniform(0.1,0.3))
#             return
#
#
#     def game_over(self):
#
#
# @mine_sweep.handle()
# async def _(event:GroupMessageEvent,state:T_State,)





