from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *
legend_box = on_command("legend_box", aliases={"开神器盒子", })


@legend_box.handle()
async def _(event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    state["user_id"] = event.user_id
    state["group_id"] = event.group_id
    auth = authority(event.group_id, "legend_box")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await legend_box.finish("请在1:00——10:00期间使用本系统")
    arg = arg.extract_plain_text().strip()
    if arg:
        state["number"] = arg


@legend_box.got("number", prompt="请输入您要开启的数量：(每个盒子180金币,一次最多300个)")
async def _(event: GroupMessageEvent, state: T_State):
    num = state["number"]
    player = Person(state["user_id"], state["group_id"])
    try:
        num = int(str(num))
    except ValueError:
        await legend_box.finish("您输入的数量有误！")
        return
    if num > 300:
        await legend_box.finish("为防止服务器卡顿，每次最多开启300个")
        return
    if player.gold < num * 180:
        await legend_box.finish("您的金币不足")
        return
    player.gold -= num * 180
    result = sqlquery(SELECT, "legend_box", None)
    box_item = [(Item(it[1], it[2]), it[3]) for it in result]
    empty_person = Person(0, 0)
    player.query()
    for i in range(num):
        randitem = overrandom(box_item)
        player.package.setdefault(randitem.item_id, Item(randitem.item_id))
        player.package[randitem.item_id].count += randitem.count
        empty_person.package.setdefault(randitem.item_id, Item(randitem.item_id))
        empty_person.package[randitem.item_id].count += randitem.count
        del randitem
    empty_person.print_package()
    player.refresh_all()
    await legend_box.finish(MessageSegment.at(player.user_id) + "您获得的物品如下:" + MessageSegment.image(
        f"file:///{__file__.strip('__init__.py')}../temp/temp_bag.png"))
    del empty_person
    return


labyrinth = on_command("labyrinth", aliases={"迷宫寻宝", "模拟迷宫寻宝"})


@labyrinth.handle()
async def _(event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    state["user_id"] = event.user_id
    state["group_id"] = event.group_id
    auth = authority(event.group_id, "labyrinth")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await labyrinth.finish("请在1:00——10:00期间使用本系统")
    arg = arg.extract_plain_text().strip()
    if arg:
        state["number"] = arg


@labyrinth.got("number", prompt="请输入您要开启的数量：(每次寻宝300金币,一次最多300个)")
async def _(event: GroupMessageEvent, state: T_State):
    num = state["number"]
    player = Person(state["user_id"], state["group_id"])
    try:
        num = int(str(num))
    except ValueError:
        await labyrinth.finish("您输入的数量有误！")
        return
    if num > 300:
        await labyrinth.finish("为防止服务器卡顿，每次最多开启300个")
        return
    if player.gold < num * 300:
        await labyrinth.finish("您的金币不足")
        return
    player.gold -= num * 300
    result = sqlquery(SELECT, "labyrinth", None)
    box_item = [(Item(it[1], it[2]), it[3]) for it in result]
    empty_person = Person(0, 0)
    player.query()
    for i in range(num):
        randitem = overrandom(box_item)
        player.package.setdefault(randitem.item_id, Item(randitem.item_id))
        player.package[randitem.item_id].count += randitem.count
        empty_person.package.setdefault(randitem.item_id, Item(randitem.item_id))
        empty_person.package[randitem.item_id].count += randitem.count
        del randitem
    empty_person.print_package()
    player.refresh_all()
    await labyrinth.finish(MessageSegment.at(player.user_id) + "您获得的物品如下:" + MessageSegment.image(
        f"file:///{__file__.strip('__init__.py')}../temp/temp_bag.png"))
    del empty_person
    return