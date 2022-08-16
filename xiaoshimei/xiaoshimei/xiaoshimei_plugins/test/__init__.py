import random
import requests
from PIL import Image
from io import BytesIO
import json


from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *

test = on_command("测试")


@test.handle()
async def call_daily_league(event: GroupMessageEvent):
    record_list = ["yarimasune", "lengbingbing", "testify","grievous_lady","senpai"]
    rand = random.randint(0,len(record_list)-1)
    await test.send(MessageSegment.record(f"file:///{__file__.strip('__init__.py')}{record_list[rand]}.wav"))


# req = on_request()
#
#
# @req.handle()
# async def _(event:GroupRequestEvent,bot:Bot):
#     comment = event.comment
#     weapon = ["烈火","轰天","神风","雷霆","医用工具箱","黑白家电","司马砸缸","牛顿水果篮","畅通利器"]
#     weapon_head = ["真·","极·","真","极"]
#     weapon2 = ["收割者之镰","棒棒糖","加农神炮","捣蛋鬼","冰雪神杖","玛雅蛇杖","伯爵之剑","花之恋","守护者法杖"]
#     weapon3 = ["爱心回力标","牛头怪","远古竹枪"]
#     weapon_head3 = ["","真","真·"]
#     weapon4 = ["极·爱心回力标","幸运神","战神","龙枪","弹王回力标"]
#     weapon5 = ["真·疯狂小鸡","真·幻翎","潘多拉魔琴","真疯狂小鸡","天天向上"]
#     weapon6 = ["飞天跑车","雪之爱","圣诞派","飞天帚","圣火之炬","魔力水枪","工作狂","热熔粒子针"]
#     weapon_head6 = ["极","极·"]
#     permit = [b + a for a in weapon for b in weapon_head] + weapon2 + [b + a for a in weapon3 for b in weapon_head3] + weapon4 + weapon5 + [b + a for a in weapon6 for b in weapon_head6]
#     if comment in permit:
#         await event.approve(bot)
#     else:
#         await event.reject(bot,"请正确填写武器名称（可以不包括“·”）")


test2 = on_regex("[要来][一两12][份张].*[se涩色]图$")


@test2.handle()
async def _(bot:Bot,event:Event):
    arg = event.get_plaintext()
    user_id = event.get_user_id()
    args = re.findall(r"[要来]([一两12])[份张](.*)[se涩色]图",arg)
    num = 2 if args[0] in ["2","两"] else 1
    tag = None if len(args) == 1 else arg[1]
    data = {"size":"original","num":num}
    if tag:
        data["tag"] = tag
    resp = requests.post(url="https://api.lolicon.app/setu/v2",data=json.dumps(data))
    resp_data = json.loads(resp.text)["data"][0]
    img_url = resp_data["urls"]["original"]
    title = resp_data["title"]
    author = resp_data["author"]
    pid = resp_data["pid"]
    img = requests.get(img_url)
    bio = BytesIO(img.content)
    await bot.send_private_msg(user_id=int(user_id),message=f"title:{title} \nauthor:{author}\npid:{pid}" + MessageSegment.image(bio))