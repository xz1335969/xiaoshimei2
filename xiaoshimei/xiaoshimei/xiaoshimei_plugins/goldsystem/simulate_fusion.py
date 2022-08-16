import random

from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *
import copy

simulate_fusion = on_command("simulate_fusion", aliases={"模拟熔炼", })


@simulate_fusion.handle()
async def _(event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    user_id = event.user_id
    group_id = event.group_id
    player = Person(user_id, group_id)
    auth = authority(event.group_id, "fusion")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await simulate_fusion.finish("请在1:00——10:00期间使用本系统")
    state["player"] = player
    if arg.extract_plain_text().strip() == "批量":
        state["type"] = 1
    player.query()
    empty_player = Person(0, 0)
    for item in player.package.values():
        if item.count >= 4 and item.fusion_id != 0:
            empty_player.package[item.item_id] = copy.deepcopy(item)
    if not len(empty_player.package):
        await simulate_fusion.finish("您没有可以熔炼的物品")
    state["prompt"] = empty_player.print_package_txt()
    state["empty_player_package"] = empty_player.package


@simulate_fusion.got("item_id", prompt=MessageTemplate("{prompt}"))
async def _(event: GroupMessageEvent, state: T_State):
    player = state["player"]
    item_id = int(state["item_id"])
    empty_player_package = state["empty_player_package"]
    if item_id not in empty_player_package.keys():
        await simulate_fusion.finish("物品数量不足")
    else:
        item = player.package[item_id]
        if not state.get("type", 0):
            state["times"] = 1
        state["item"] = item


@simulate_fusion.got("times", prompt="请输入熔炼次数（为防止刷屏，超过30次将自动折叠）")
async def _(event: GroupMessageEvent, state: T_State,bot:Bot):
    player = state["player"]
    item = state["item"]
    item_product = player.package.setdefault(item.fusion_id, Item(item.fusion_id))
    if state["times"] == "全部":
        times = item.count // 4
    else:
        times = int(state["times"])
    report = []
    if times > 30 or item.fusion_probability == 100:
        fusion_sum = 0
        for i in range(times):
            if item.count < 4:
                break
            else:
                item.count -= 4
                rand = random.randint(0, 99)
                if rand < item.fusion_probability:
                    item_product.count += 1
                    fusion_sum += 1
        report.append(f"熔炼完成，得到{fusion_sum}个{item_product.name}")
    else:
        # 成功率不到100，分条显示结果
        for i in range(times):
            if item.count < 4:
                report.append("物品数量不足")
                break
            else:
                item.count -= 4
                rand = random.randint(0, 99)
                if rand < item.fusion_probability:
                    item_product.count += 1
                    report.append(f'恭喜您熔炼成功，获得一个{item_product.name}')
                else:
                    report.append("熔炼失败.")
    player.refresh_all()
    await simulate_fusion.finish("\n".join(report))


