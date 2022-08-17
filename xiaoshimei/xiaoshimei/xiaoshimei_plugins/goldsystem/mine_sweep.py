from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

mine_sweep = on_command("mine_sweep",aliases={"扫雷游戏","挖挖乐2"})


class MineSweepGame:
    def __init__(self,gold,mine = 50):
        self._GAME_OVER = 1
        self._GET_GOLD = 2
        self._GET_ITEM = 3
        self.initgold = gold
        mine_map = [0]*100
        i = 0
        while sum(mine_map)<= mine - 2:
            mine_map[i] += random.randint(1,3)
            i += 1
        while sum(mine_map)<= mine:
            mine_map[i] += random.randint(1,50-sum(mine_map))
            i += 1
        for j in range(i,i+5):
            mine_map[j] = "item"
        i += 10
        for j in range(i,i+20):
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
        def remove(x:list|any,y:list):
            for _i in x:
                if _i in y:
                    y.remove(_i)
                else:
                    continue
            return y

        for i in range(100):
            x = i % 10
            y = i // 10
            block_list = [-11,-10,-9,-1,1,9,10,11]
            if x-1 <0:
                ls = [-11,1,9]
                remove(ls,block_list)
            if x+1 > 9:
                ls = [-9,1,11]
                remove(ls,block_list)
            if y-1<0:
                ls = [-11,-10,-9]
                remove(ls, block_list)
            if y+1>9:
                ls = [9,10,11]
                remove(ls, block_list)

            around_mine_num[i] = sum([mine_map[i+j] for j in block_list])
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
        around_mine_num =self.around_mine_num
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


    def sweep(self,block:int):
        """
        点击地址
        :param block: 挖某个格子
        :return:结果
        """
        chosen_block = self.mine_map[block]
        if type(chosen_block) == int and chosen_block > 0:
            self.game_over()
            return self._GAME_OVER
        elif chosen_block == "empty":
            self.mine_map[block] = 0
            return 0
        elif chosen_block == "gold":
            self.gold += int(self.initgold * random.uniform(0.1,0.3))
            return


    def game_over(self):

        return


@mine_sweep.handle()
async def _(event:GroupMessageEvent,state:T_State,):
    pass