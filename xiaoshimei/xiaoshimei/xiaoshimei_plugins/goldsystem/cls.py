import os, random, datetime
from .._globals import TYPELIST, EXTRA_MODULES, EXTRA_MODULES3, EXTRA_MODULES2, randomlist, overrandom
from . import createImage
from nonebot import on_command, get_bot,on_message,on_keyword,on_regex,on_notice,on_request
from nonebot.adapters import Event, Message, MessageTemplate
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, PrivateMessageEvent, GroupMessageEvent, Bot, \
    GROUP_ADMIN, GROUP_OWNER, GROUP_MEMBER,RequestEvent,GroupRequestEvent
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.params import State, Depends, CommandArg, Arg, ArgPlainText
from nonebot.rule import to_me
import re
import pymysql

SELECT = 0
UPDATE = 1
INSERT = 2
DELETE = 3


def sqlquery(query_type: int, table: str, field: dict = None, *args, **kwargs):
    """
    :param query_type: SELECT,UPDATE,INSERT,DELETE
    :param table: 表名
    :param field: 查询条件（WHERE后面的）
    :param args: 查询内容，SELECT写列名（list），UPDATE写等号前后数值组成的元组，INSERT写两个元组(A1,A2,A3) VALUES（B1,B2,B3）
    :param kwargs: 查询条件附加：（WHERE xxx in yyy)
    :return: SELECT返回查询结果，其他返回 1
    """
    conn = pymysql.connect(host='localhost', user='root', password='xz123456', database='xiaoshimei',
                           charset='utf8mb4')
    cursor = conn.cursor()
    if query_type == 0:
        if len(args) == 0:
            column = "*"
        else:
            column = ",".join(args)
        if field is None:
            sql = f"SELECT {column} FROM {table}"
        else:
            if len(kwargs) == 0:
                fields = " AND ".join([f"{k} = {v}" for k, v in field.items()])
            else:
                fields = " AND ".join(
                    [f"{k} = {v}" for k, v in field.items()] + [f"{k} {v}" for k, v in kwargs.items()])
            sql = f"SELECT {column} FROM {table} WHERE {fields}"
        cursor.execute(sql)
        report = cursor.fetchall()
        conn.close()
        return report
    elif query_type == 1:
        column = ",".join([f"{k}={v}" for (k, v) in args])
        if len(kwargs) == 0:
            fields = " AND ".join([f"{k}={v}" for k, v in field.items()])
        else:
            fields = " AND ".join(
                [f"{k}={v}" for k, v in field.items()] + [f"{k} {v}" for k, v in kwargs.items()])
        sql = f"UPDATE {table} SET {column} WHERE {fields}"
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return 1
    elif query_type == 2:
        sql = f"INSERT INTO {table} ({','.join([str(i) for i in args[0]])}) VALUES ({','.join([str(i) for i in args[1]])})"
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return 1
    else:
        if len(kwargs) == 0:
            fields = " AND ".join([f"{k}={v}" for k, v in field.items()])
        else:
            fields = " AND ".join(
                [f"{k}={v}" for k, v in field.items()] + [f"{k} {v}" for k, v in kwargs.items()])
        sql = f"DELETE FROM {table} WHERE {fields}"
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return 1


def get_qq(cq_str: str) -> int:
    qq = re.findall(r"\[CQ:at,qq=(\w+)]", cq_str)
    return qq[0]


def authority(group_id, extra_name=None) -> int:
    if extra_name is None:
        auth = sqlquery(SELECT, "authority", {"group_id": group_id}, extra_name)
        if auth is None:
            sqlquery(INSERT, "authority", None, ("group_id",), (group_id,))
            authority(group_id, None)
    else:
        auth = sqlquery(SELECT, "authority", {"group_id": group_id}, extra_name)[0]
    return auth


def change_authority(group_id,extra_name:list[str],is_open:int):
    args = [(k,v) for (k,v) in zip(extra_name,[is_open]*len(extra_name))]
    authority(group_id,"group_id")
    sqlquery(UPDATE,"authority",{"group_id":group_id},*args)
    return "模块开启成功" if is_open else "模块关闭成功"

class Item:
    def __init__(self, item_id: int, count=0, price=0):
        self.uni_id = None
        self.item_id = item_id
        result = sqlquery(SELECT, "item_details", {"item_id": self.item_id})
        if not result:
            print(item_id)
            print("***************************************************")
            raise Exception("NO Item Index ERROR")
        else:
            result = result[0]
        self.name = result[1]
        self.type = result[2]
        self.property1 = result[3]
        self.property2 = result[4]
        self.fusion_id = result[5]
        self.fusion_probability = result[6]
        self.count = count
        self.price = price
        self.shop_limit = None
        self.bought_times = None
        self.limit_type = 0


class Weapon(Item):
    def __init__(self, weapon_id: int):
        self.weapon_id = weapon_id
        result = sqlquery(SELECT, "weapon", {"weapon_id": self.weapon_id})[0]
        self.item_id = result[1]
        self.uni_id = result[2]
        self.player_id = result[3]
        self.strength_lvl = result[4]
        self.durability = result[5]
        Item.__init__(self, self.item_id)
        self.baseDamage = self.property1
        self.quality = self.property2
        self.damage = int(self.baseDamage * (1.1 ** self.strength_lvl))

    def refresh(self):
        sqlquery(UPDATE, "weapon", {"weapon_id": self.weapon_id},
                 (("strength_lvl", self.strength_lvl), ("durability", self.durability)))

    def destroy(self):
        sqlquery(DELETE, "weapon", {"weapon_id": self.weapon_id})


class Shield(Item):
    def __init__(self, weapon_id: int):
        self.weapon_id = weapon_id
        result = sqlquery(SELECT, "weapon", {"weapon_id": self.weapon_id})[0]
        self.item_id = result[1]
        self.uni_id = result[2]
        self.user_id = result[3]
        self.strength_lvl = result[4]
        Item.__init__(self, self.item_id)
        self.baseGuard = self.property1
        self.quality = self.property2
        self.guard = int(self.baseGuard * (1.1 ** self.strength_lvl))

    def refresh(self):
        sqlquery(UPDATE, "weapon", {"weapon_id": self.weapon_id}, (("strength_lvl", self.strength_lvl),))

    def destroy(self):
        sqlquery(DELETE, "weapon", {"weapon_id": self.weapon_id})


# user_detail
# player_id  user_id  group_id  gold  rob_ban


class Person:
    def __init__(self, user_id: int, group_id: int, player_id=None):
        if user_id == 0:
            self.package = {}
            self.gold = 0
            self.weapon = []
            self.shield = []
            self.player_id = 0
        else:
            if player_id is not None:
                result = sqlquery(SELECT, "user_detail", {"player_id": player_id}, "user_id", "gold", "rob_ban",
                                  "is_superuser", "vip_end_time", "group_id")
                if result is None:
                    raise Exception("No such player_id")
                else:
                    result = result[0]
                    self.user_id = result[0]
                    self.group_id = result[5]
                    self.gold = result[1]
                    self.rob_ban = result[2]
                    self.is_superuser = result[3]
                    self.vip_end_time = result[4]
                now = datetime.datetime.now()
                now.strftime("%Y-%m-%d %H:%M:%S")
                self.is_vip = 0 if now > self.vip_end_time else 1
                self.user_id = user_id
                self.group_id = group_id
                self.package = {}
                self.weapon = []
                self.shield = []
            else:
                result = sqlquery(SELECT, "user_detail", {"user_id": user_id, "group_id": group_id}, "player_id",
                                  "gold", "rob_ban", "is_superuser", "vip_end_time")
                # if result is None:
                if len(result) == 0:
                    sqlquery(INSERT, "user_detail", None, ("user_id", "group_id", "gold", "rob_ban", "is_superuser"),
                             (user_id, group_id, 0, 0, 0))
                    result = sqlquery(SELECT, "user_detail", {"user_id": user_id, "group_id": group_id}, "player_id",
                                      "gold", "rob_ban", "is_superuser", "vip_end_time")
                    result = result[0]
                    self.player_id = result[0]
                    self.gold = result[1]
                    self.rob_ban = result[2]
                    self.is_superuser = result[3]
                    self.vip_end_time = result[4]
                else:
                    result = result[0]
                    self.player_id = result[0]
                    self.gold = result[1]
                    self.rob_ban = result[2]
                    self.is_superuser = result[3]
                    self.vip_end_time = result[4]
                now = datetime.datetime.now()
                self.is_vip = 0 if now > self.vip_end_time else 1
                self.user_id = user_id
                self.group_id = group_id
                self.package = {}
                self.weapon = []
                self.shield = []

    def query(self, item_id_list=None, item_type_list=None) -> dict[int, Item]:
        pack = {}
        if not item_id_list:
            area = ""
        else:
            area = f" AND item_id in ({','.join([str(i) for i in item_id_list])})"
        if not item_type_list:
            types = ""
        else:
            types = f" AND type in ({','.join([str(TYPELIST[i]) for i in item_type_list])})"
        conn = pymysql.connect(host='localhost', user='root', password='xz123456', database='xiaoshimei',
                               charset='utf8mb4')
        cursor = conn.cursor()
        sql = f'SELECT * FROM user_package WHERE player_id = {self.player_id} AND count > 0' + area + types
        cursor.execute(sql)
        result = cursor.fetchone()
        while result:
            item_id = result[2]
            count = result[3]
            item = Item(item_id)
            item.count = count
            item.uni_id = result[0]
            pack[item_id] = item
            result = cursor.fetchone()
        conn.close()
        self.package = pack
        return pack

    def refresh(self):
        sqlquery(UPDATE, "user_detail", {"player_id": self.player_id},
                 ("gold", self.gold), ("is_superuser", self.is_superuser), ("rob_ban", self.rob_ban),
                 ("vip_end_time", f'\'{self.vip_end_time.strftime("%Y-%m-%d %H:%M:%S")}\'')
                 )
        return 1

    def refresh_all(self):
        self.refresh()
        for item in self.package.values():
            if not sqlquery(SELECT, "user_package", {"player_id": self.player_id, "item_id": item.item_id}):
                sqlquery(INSERT, "user_package", None,
                         ("player_id", "item_id", "count", "type"),
                         (self.player_id, item.item_id, item.count, item.type))
            else:
                sqlquery(UPDATE, "user_package", {"item_id": item.item_id, "player_id": self.player_id},
                         ("count", item.count), ("type", item.type))
        return 1

    # user_package
    # uni_id  player_id  item_id  count  type

    # weapon
    # weapon_id  item_id  uni_id  player_id  strength_lvl
    # 自增

    def weapon_query(self, item: Item = None, *args):
        weapons = []
        conn = pymysql.connect(host='localhost', user='root', password='xz123456', database='xiaoshimei',
                               charset='utf8mb4')
        if item is None:
            field = self.query(None, ["weapon"])
        else:
            if len(args):
                field = [item] + [i for i in args]
            else:
                field = [item]
        if len(field) == 0:
            return None
        for item in field.values():
            if item.count == 0:
                continue
            sql = f"SELECT * FROM weapon WHERE uni_id = {item.uni_id}"
            cursor = conn.cursor()
            cursor.execute(sql)
            for i in range(item.count):
                result = cursor.fetchone()
                weapon_id = result[0]
                weapon = Weapon(weapon_id)
                weapons.append(weapon)
        conn.close()
        self.weapon = weapons
        return weapons

    def shield_query(self, item: Item = None, *args):
        shields = []
        conn = pymysql.connect(host='localhost', user='root', password='xz123456', database='xiaoshimei',
                               charset='utf8mb4')
        if item is None:
            field = self.query(None, ["shield"])
        else:
            if len(args):
                field = [item] + [i for i in args]
            else:
                field = [item]
        if len(field) == 0:
            return None
        for item in field:
            if item.count == 0:
                continue
            sql = f"SELECT * FROM weapon WHERE uni_id = {item.uni_id}"
            cursor = conn.cursor()
            cursor.execute(sql)
            for i in range(item.count):
                result = cursor.fetchone()
                weapon_id = result[0]
                weapon = Weapon(weapon_id)
                shields.append(weapon)
        conn.close()
        self.shield = shields
        return shields

    def get_item(self, item: Item, count: int):
        self.package.setdefault(item.item_id, Item(item.item_id))
        self.package[item.item_id].count += count

    def signin(self) -> Message:
        _min = 50
        _max = 800
        now = datetime.datetime.now()
        self.query()
        today0 = now - datetime.timedelta(seconds=now.second, minutes=now.minute, hours=now.hour)
        today0_txt = today0.strftime('%Y-%m-%d %H:%M:%S')
        month0 = now - datetime.timedelta(minutes=now.minute, seconds=now.second, hours=now.hour, days=now.day - 1)
        month0_txt = month0.strftime('%Y-%m-%d %H:%M:%S')
        conn = pymysql.connect(host='localhost', user='root', password='xz123456', database='xiaoshimei',
                               charset='utf8mb4')
        sql = f"SELECT time FROM signin WHERE player_id= {self.player_id} AND TIME > TIMESTAMP('{today0_txt}')"
        cursor = conn.cursor()
        cursor.execute(sql)
        issigned = cursor.fetchone()
        if not issigned:
            gold_num = random.randint(_min, _max)
            self.gold += gold_num
            report = MessageSegment.at(self.user_id) + f'签到成功，获得{gold_num}金币'
            cursor2 = conn.cursor()
            sql2 = f'INSERT INTO signin (player_id) VALUES ({self.player_id})'
            cursor2.execute(sql2)
            conn.commit()
            cursor3 = conn.cursor()
            sql2 = f"SELECT time FROM signin WHERE player_id= {self.player_id} AND TIME > TIMESTAMP('{month0_txt}')"
            cursor3.execute(sql2)
            signed_times = len(cursor3.fetchall())
            if signed_times == 3:
                report = report + "\n" + "您本月已经签到3天，获得奖励：3级强化石*5"
                self.package.setdefault(203, Item(203))
                self.package[203].count += 5
            elif signed_times == 7:
                report = report + "\n" + "您本月已经签到7天，获得奖励：4级强化石*5"
                self.package.setdefault(204, Item(204))
                self.package[204].count += 5
            elif signed_times == 14:
                report = report + "\n" + "您本月已经签到14天，获得奖励：5级强化石*3"
                self.package.setdefault(205, Item(205))
                self.package[205].count += 3
            elif signed_times == 21:
                report = report + "\n" + "您本月已经签到21天，获得奖励：5级强化石*5,神恩符*3,4000金币，攻击祝福宝珠*3"
                self.package.setdefault(205, Item(205))
                self.package.setdefault(206, Item(206))
                self.package.setdefault(211, Item(211))
                self.package[205] += 5
                self.package[206] += 3
                self.package[211] += 3
                self.gold += 4000
            elif signed_times == 28:
                report = report + "\n" + "您本月已经签到28天，获得奖励：VIP*7天，VIP下商店物品8折，强化成功率提升30%"
                endtime = datetime.datetime.now() + datetime.timedelta(days=7)
                self.vip_end_time = endtime
        else:
            report = MessageSegment.at(self.user_id) + "您今天已经签到过了！"
        self.refresh_all()
        return report

    def print_package(self) -> bool:
        """
        保存图片到上一级文件夹的temp\temp_bag.png
        :return:成功返回True,不存在包裹返回False
        """
        item_num = len(self.package)
        if item_num:
            bag = createImage.init_empty_bag(item_num)
            item_list = [
                {'name': item.item_id, "count": item.count}
                for item in self.package.values()
            ]
            createImage.draw_item_by_list(bag, item_list)
            bag.save(f'{__file__.strip("__init__.py")}..\\temp\\temp_bag.png')
            return True
        else:
            raise Exception("ERROR")

    def print_package_txt(self):
        return "\n".join([f"{i.item_id}:{i.name}" for i in self.package.values()])


# now = time.strftime("%Y%m%d%H%M%S", time.localtime())
# shop
# shop_id(自增) item_id count=1 price  shop_limit  limit_type(0无限制 1总限制 2月限制 3日限制)

# shop_limit
# shop_id  player_id  bought_time  count


class Shop:
    def __init__(self, player: Person):
        self.show_list = None
        result = sqlquery(SELECT, "shop", None)
        self.goods_list = []
        self.shop_id_list = []
        self.player = player
        self.vip = player.is_vip
        result2 = sqlquery(SELECT, "shop_limit", {"player_id": player.player_id}, "shop_id", "bought_time", "count")

        def bought_times(shop_id, limit_type):
            now = datetime.datetime.now()
            summary = 0
            if limit_type == 1:
                for i in result2:
                    if i[0] == shop_id:
                        summary += i[2]
                return summary
            elif limit_type == 2:
                for i in result2:
                    bought_time = datetime.datetime.fromisoformat(i[1])
                    if i[0] == shop_id and (bought_time - now).days < 30 and bought_time.month == now.month:
                        summary += i[2]
                return summary
            elif limit_type == 3:
                for i in result2:
                    bought_time = i[1]
                    if i[0] == shop_id and (bought_time - now).days < 1 and bought_time.day == now.day:
                        summary += i[2]
                return summary
            return summary

        for good in result:
            item = Item(good[1])
            item.shop_id = good[0]
            item.count = good[2]
            item.price = int(good[3] * (1 - 0.2 * self.vip))
            item.shop_limit = good[4]
            item.limit_type = good[5]
            item.bought_times = bought_times(item.shop_id, item.limit_type)
            self.goods_list.append(item)
            self.shop_id_list.append(item.shop_id)

    def showlist(self) -> str:
        report = "您目前具有VIP资格，商店物品8折处理 \n" if self.vip else ""
        report = report + "请选择您要购买的商品编号："
        show_list = []
        for good in self.goods_list:
            if good.limit_type:
                shop_limit = good.shop_limit
                bought_time = good.bought_times
                rest = shop_limit - bought_time
                if rest == 0:
                    continue
                limit_type_txt = [None, "", "本月", "今日"]
                if good.limit_type == 0:
                    rest_txt = ''
                else:
                    rest_txt = f"({limit_type_txt[good.limit_type]}剩余{rest})"
            else:
                rest_txt = ''
            shopid = good.shop_id
            num = f" *{good.count}" if good.count > 1 else ""
            name = good.name
            price = good.price
            report = report + f"\n{shopid}: {name}{num}({price}金币){rest_txt}"
            show_list.append(good.shop_id)
        self.show_list = show_list
        return report


