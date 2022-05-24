import os
import re
import time

from nonebot import on_endswith, on_command, on_regex
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.params import RegexDict
from nonebot.typing import T_State

from utils.character_alias import get_id_by_alias
from utils.decorator import exception_handler
from utils.message_util import MessageBuild, match_alias
from .abyss_rate_draw import draw_rate_rank, draw_teams_rate
from .blue import get_blue_pic

__usage__ = '''
1.[xx角色攻略]查看西风驿站出品的角色一图流攻略
2.[xx角色材料]查看惜月出品的角色材料统计
3.[xx参考面板]查看blue菌hehe出品的参考面板攻略
4.[xx收益曲线]查看blue菌hehe出品的收益曲线攻略
*感谢来自大佬们的授权。角色支持别名查询
5.[今日/明日/周x材料]查看每日角色天赋材料和武器突破材料表
6.[深渊登场率]查看2.6深渊角色登场率
7.[深渊上半/下半阵容出场率]查看2.6深渊阵容出场率
'''
__help_version__ = '1.0.2'

res_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res')

guide = on_endswith('角色攻略', priority=8)
material = on_endswith('角色材料', priority=6, block=True)
attribute = on_endswith('参考面板', priority=6, block=True)
attribute2 = on_endswith('收益曲线', priority=6, block=True)
daily_material = on_endswith(('材料', '天赋材料', '突破材料'), priority=6, block=True)
abyss_rate = on_command('syrate', aliases={'深渊登场率', '深境螺旋登场率', '深渊登场率排行', '深渊排行'}, priority=6, block=True)
abyss_team = on_regex(r'^(深渊|深境螺旋)(?P<floor>上半|下半)阵容(排行|出场率)?$', priority=5, block=True)
weapon_guide = on_endswith('武器攻略', priority=6, block=True)
monster_map = on_endswith('原魔图鉴', priority=6, block=True)


@guide.handle()
@exception_handler()
async def genshin_guide(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('角色攻略', '').strip()
    realname = get_id_by_alias(name)
    if name in ['风主', '岩主', '雷主'] or realname:
        name = realname[1][0] if name not in ['风主', '岩主', '雷主'] else name
        await guide.finish(await MessageBuild.StaticImage(url=f'LittlePaimon/XFGuide/{name}.jpg'))
    else:
        await guide.finish(f'没有找到{name}的攻略', at_sender=True)


@material.handle()
@exception_handler()
async def genshin_material(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('角色材料', '').strip()
    realname = get_id_by_alias(name)
    if name in ['夜兰', '久岐忍', '鹿野院平藏'] or realname:
        name = realname[1][0] if realname else name
        await material.finish(await MessageBuild.StaticImage(f'LittlePaimon/RoleMaterials/{name}材料.jpg'))
    else:
        await material.finish(f'没有找到{name}的材料', at_sender=True)


@attribute.handle()
@exception_handler()
async def genshinAttribute(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('参考面板', '').strip()
    realname = get_id_by_alias(name)
    if name in ['风主', '岩主', '雷主'] or realname:
        name = realname[1][0] if name not in ['风主', '岩主', '雷主'] else name
        img = await get_blue_pic(name)
        await attribute.finish(img)
    else:
        await attribute.finish(f'没有找到{name}的参考面板', at_sender=True)


@attribute2.handle()
@exception_handler()
async def genshinAttribute2(event: MessageEvent):
    name: str = event.message.extract_plain_text().replace('收益曲线', '').strip()
    realname = get_id_by_alias(name)
    if name in ['风主', '岩主', '雷主'] or realname:
        name = realname[1][0] if name not in ['风主', '岩主', '雷主'] else name
        await attribute2.finish(await MessageBuild.StaticImage(url=f'LittlePaimon/blue/{name}.jpg'))
    else:
        await attribute2.finish(f'没有找到{name}的收益曲线', at_sender=True)


@daily_material.handle()
@exception_handler()
async def daily_material_handle(event: MessageEvent):
    week: str = event.message.extract_plain_text().replace('材料', '').replace('天赋材料', '').replace('突破材料', '').strip()
    if week:
        find_week = re.search(r'(?P<week>今日|今天|现在|明天|明日|后天|后日|周一|周二|周三|周四|周五|周六|周日)', week)
        if find_week:
            if find_week.group('week') in ['今日', '今天', '现在']:
                week = time.strftime("%w")
            elif find_week.group('week') in ['明日', '明天']:
                week = str(int(time.strftime("%w")) + 1)
            elif find_week.group('week') in ['后日', '后天']:
                week = str(int(time.strftime("%w")) + 2)
            elif find_week.group('week') in ['周一', '周四']:
                week = '1'
            elif find_week.group('week') in ['周二', '周五']:
                week = '2'
            elif find_week.group('week') in ['周三', '周六']:
                week = '3'
            else:
                week = '0'
            if week == "0":
                await daily_material.finish('周日所有材料都可以刷哦!', at_sender=True)
            elif week in ['1', '4']:
                url = 'LittlePaimon/DailyMaterials/周一周四.jpg'
            elif week in ['2', '5']:
                url = 'LittlePaimon/DailyMaterials/周二周五.jpg'
            else:
                url = 'LittlePaimon/DailyMaterials/周三周六.jpg'
            await daily_material.finish(await MessageBuild.StaticImage(url=url))


@abyss_rate.handle()
@exception_handler()
async def abyss_rate_handler(event: MessageEvent):
    abyss_img = await draw_rate_rank()
    await abyss_rate.finish(abyss_img)


@abyss_team.handle()
@exception_handler()
async def abyss_team_handler(event: MessageEvent, reGroup=RegexDict()):
    abyss_img = await draw_teams_rate(reGroup['floor'])
    await abyss_team.finish(abyss_img)


def create_choice_command(endswith: str, type_: str, url: str, file_type: str = 'jpg'):
    command = on_endswith(endswith, priority=6, block=False)

    @command.handle()
    async def _(event: MessageEvent, state: T_State):
        name = event.message.extract_plain_text().replace(endswith, '').strip()
        if name:
            state['name'] = name

    @command.got('name', prompt=f'请把要查询的{endswith[0:2]}告诉我哦~')
    async def _(event: MessageEvent, state: T_State):
        name = state['name']
        if isinstance(name, Message):
            name = name.extract_plain_text().strip()
            if name == 'q':
                await command.finish()
        finally_name = await match_alias(name, type_)
        if isinstance(finally_name, str):
            await command.finish(await MessageBuild.StaticImage(url=url + finally_name + '.' + file_type))
        elif isinstance(finally_name, list):
            if not finally_name:
                await command.finish(f'没有该{endswith[0:2]}的信息哦，问一个别的吧~')
            else:
                if 'choice' not in state:
                    msg = f'你要找的{endswith[0:2]}是哪个呀：\n'
                    msg += '\n'.join([f'{int(i) + 1}. {name}' for i, name in enumerate(finally_name)])
                    await command.send(msg + '\n回答\"q\"可以取消查询')
                state['match_alias'] = finally_name

    @command.got('choice')
    async def _(event: MessageEvent, state: T_State):
        match_alias = state['match_alias']
        choice = state['choice']
        choice = choice.extract_plain_text().strip()
        if choice == 'q':
            await command.finish()
        if choice.isdigit() and (1 <= int(choice) <= len(match_alias)):
            await command.finish(
                await MessageBuild.StaticImage(url=url + match_alias[int(choice) - 1] + '.' + file_type))
        if choice not in match_alias:
            state['times'] = state['times'] + 1 if 'times' in state else 1
            if state['times'] >= 3:
                await command.finish(f'看来旅行者您有点神志不清哦(，下次再问派蒙吧' + MessageSegment.face(146))
            elif state['times'] == 1:
                await command.reject(f'请旅行者从上面的{endswith[0:2]}中选一个问派蒙\n回答\"q\"可以取消查询')
            elif state['times'] == 2:
                await command.reject(f'别调戏派蒙啦，快选一个吧，不想问了麻烦回答\"q\"！')
        await command.finish(await MessageBuild.StaticImage(url=url + choice + '.' + file_type))


create_choice_command('原魔图鉴', 'monsters', 'LittlePaimon/MonsterMaps/', 'jpg')
create_choice_command('武器攻略', 'weapons', 'LittlePaimon/WeaponGuild/', 'png')
