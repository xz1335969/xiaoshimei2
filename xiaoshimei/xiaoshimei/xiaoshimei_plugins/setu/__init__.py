import random
import requests
from PIL import Image
from io import BytesIO
import json


from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *

test = on_command("给爷唱一段",rule=to_me())


@test.handle()
async def _(event: GroupMessageEvent):
    record_list = ["yarimasune", "lengbingbing", "testify","grievous_lady","senpai"]
    rand = random.randint(0,len(record_list)-1)
    await test.send(MessageSegment.record(f"file:///{__file__.strip('__init__.py')}{record_list[rand]}.wav"))


setu = on_regex("[要来][一两12]?[份张].*[(se)涩色]图$",rule=to_me(),priority=3)
setu2 = on_regex("[要来][一1]?[份张]小师妹的?[(se)涩色]图$",priority=2)


@setu.handle()
async def _(bot:Bot,event:MessageEvent):
    arg = event.get_plaintext()
    user_id = event.get_user_id()
    args = re.findall(r"[要来]([一两12]?)[份张](.*)[se涩色]图",arg)
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
    await setu.finish()


@setu2.handle()
async def _(event:GroupMessageEvent):
    img = "file:///" + __file__.strip("__init__.py") + "..\\basic\\resources\\heisi.jpg"
    await setu2.finish(MessageSegment.image(img))



