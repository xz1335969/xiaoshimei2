from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *
from nonebot import require

scheduler = require("nonebot_plugin_apscheduler").scheduler


async def test():
    bot = get_bot("2842320249")
    timedelta = datetime.datetime(2022,8,15,19,30,0) - datetime.datetime.now()
    hours = timedelta.seconds // 3600
    minutes = (timedelta.seconds // 60) % 60
    await bot.call_api("send_group_msg", group_id=817466507,message = f"还有{hours}小时{minutes}分钟就要联赛啦，请做好准备!")

scheduler.add_job(test,"cron",second = 0,day_of_week = "mon-fri")


