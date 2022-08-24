from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

mine_sweep = on_command("mine_sweep", aliases={"扫雷游戏", "挖挖乐2"})


class MineSweepGame:
    def __init__(self, gold, mine=50):
        self._GAME_OVER = 1
        self._GET_GOLD = 2
        self._GET_ITEM = 3
        self.initgold = gold
        self.item = 0
        self.status = 0
        mine_map = [0] * 100
        i = 0
        while sum(mine_map) <= mine - 2:
            mine_map[i] += random.randint(1, 3)
            i += 1
        while sum(mine_map) <= mine:
            mine_map[i] += random.randint(1, 50 - sum(mine_map))
            i += 1
        for j in range(i, i + 5):
            mine_map[j] = "item"
        i += 10
        for j in range(i, i + 20):
            mine_map[j] = "gold"
        j += 1
        while j < 100:
            mine_map[j] = "empty"
            j += 1
        randomlist(mine_map)
        self.mine_map = mine_map
        self.gold = 0
        around_mine_num = [0] * 100
        map(lambda x: 0 if isinstance(x, str) else x, mine_map)

        def remove(x: list | any, y: list):
            for _i in x:
                if _i in y:
                    y.remove(_i)
                else:
                    continue
            return y

        for i in range(100):
            x = i % 10
            y = i // 10
            block_list = [-11, -10, -9, -1, 1, 9, 10, 11]
            if x - 1 < 0:
                ls = [-11, 1, 9]
                remove(ls, block_list)
            if x + 1 > 9:
                ls = [-9, 1, 11]
                remove(ls, block_list)
            if y - 1 < 0:
                ls = [-11, -10, -9]
                remove(ls, block_list)
            if y + 1 > 9:
                ls = [9, 10, 11]
                remove(ls, block_list)

            around_mine_num[i] = sum([mine_map[i + j] for j in block_list])
        self.around_mine_num = around_mine_num

    def show(self):
        img = Image.new("RGBA", (450, 450), "#FFFFFF")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("msyh.ttc", 18)
        font2 = ImageFont.truetype("msyh.ttc", 28)

        for x in range(11):
            draw.line([x * 42 + 28, 28, x * 42 + 28, 450], fill="black", width=2)
            draw.line([28, x * 42 + 28, 450, x * 42 + 28], fill="black", width=2)

        for i in range(10):
            item = chr(i + 65)
            draw.text((41 + 43 * i, 2), text=item, font=font, fill="black")
            draw.text((7, 41 + 42 * i), text=str(i), font=font, fill="black")
        mine_map = self.mine_map
        around_mine_num = self.around_mine_num
        for x in range(10):
            for y in range(10):
                if mine_map[10 * y + x] == 0:
                    if around_mine_num[10 * y + x] == 0:
                        draw.text((36 + 42 * x, 36 + 42 * y), str(around_mine_num[10 * y + x]), fill="black",
                                  font=font2)
                else:
                    draw.rectangle((x * 42 + 30, y * 42 + 30, x * 42 + 69, y * 42 + 69), fill="#bbbbbb")
        bio = BytesIO()
        img.save(bio)
        return bio

    def __str__(self):
        return """扫雷游戏，挖挖乐的升级版、
        扫雷说明：10*10的块中一共有50个雷，5个物品格子和20个金币格子。每个格子最多有三个雷，所在格子的数字代表周围8格雷的数量之和，请尝试找出全部的雷吧。踩到地雷游戏结束，你可以随时发送“取消”来结束游戏，获得你的所有物品的一半"""

    def sweep(self, block: int):
        """
        点击地址
        :param block: 挖某个格子
        :return:结果
        """
        chosen_block = self.mine_map[block]
        if type(chosen_block) == int and chosen_block > 0:
            self.status = 1
            self.game_over()
            return self._GAME_OVER
        elif chosen_block == "empty":
            self.mine_map[block] = 0
            return 0
        elif chosen_block == "gold":
            self.gold += int(self.initgold * random.uniform(0.1, 0.3))
            return self._GET_GOLD
        elif chosen_block == "item":
            self.item += 1
            return self._GET_ITEM
        elif chosen_block == 0:
            return 4

    def game_over(self):
        if self.status:
            return self.gold, self.item
        else:
            return


@mine_sweep.handle()
async def _(event: GroupMessageEvent, state: T_State):
    user_id = event.user_id
    group_id = event.group_id
    player = Person(user_id, group_id)
    state["player"] = player
    auth = authority(group_id, "mine_sweep")
    if auth == 0:
        return
    elif auth == 2:
        if not 1 < datetime.datetime.now().hour < 10:
            await mine_sweep.finish("请在1:00——10:00期间使用本系统")
    gold = get_parameter(group_id, "mine_sweep")
    if gold:
        state["gold"] = gold


@mine_sweep.got("gold", prompt="请输入您要使用的金币")
async def _(event: GroupMessageEvent, state: T_State):
    if isinstance(state["gold"], str):
        state["gold"] = int(state["gold"])
        state["confirm"] = 1


@mine_sweep.got("confirm", prompt="本次使用的金币为{gold}，是否继续")
async def _(event: GroupMessageEvent, state: T_State):
    if state["confirm"] == "否":
        await mine_sweep.finish("已取消")
    else:
        player = state["player"]
        mine_sweep_gold = state["gold"]
        if player.gold < mine_sweep_gold:
            await mine_sweep.finish("您的金币不足")
        else:
            player.gold -= mine_sweep_gold
            state["game"] = MineSweepGame(state["gold"])


items = '1-4,10-13,15-17,20-28,30-38,40-41,44-46,70-75,201-208,211-211,221-226,231-236,301-301'
items = items.split(",")
item_list = []
for i in items:
    j = i.split("-")
    for t in range(int(j[0]), int(j[1]) + 1):
        item_list.append(t)


@mine_sweep.got("block", prompt="请输入您选择的格子，字母在前，用空格隔开，输入“取消”停止。例如：A1 B3")
async def _(event: GroupMessageEvent, state: T_State):
    game = state["game"]
    player = state["player"]
    block = state["block"].split(" ")
    if block[0] == "取消":
        await mine_sweep.finish("取消")
        pass
    else:
        report = ""
        for i in block:
            x = ord(i[0]) - 65 if ord(i[0]) < 75 else ord(i[0]) - 97
            y = int(i[1])
            result = game.sweep(10 * y + x)
            if result == 0:
                pass
            if result == 1:
                report = "对不起，您踩到了地雷，您去世了，物品全部丢失"
                await mine_sweep.finish(report)
                return
            if result == 2:
                report += "恭喜您挖到了一堆金币\n"  # 待完善
            if result == 3:
                report += "恭喜您挖到了一个物品\n"  # 待完善
            if result == 4:
                report += f"{i}这个格子已经被挖过了\n"
        await mine_sweep.send(MessageSegment.image(game.show()))
        await mine_sweep.reject(report + "请输入您选择的格子，字母在前，用空格隔开，输入“取消”停止。例如：A1 B3")

#  游戏结束还没写