from pygal_maps_world.maps import World
# 颜色相关
from pygal.style import RotateStyle
from pygal.style import LightColorizedStyle

from CountryCode import *
import shelve
import pandas


def get_country_code(country_name):
    """
    根据国家名返回两位国别码
    """
    all_code = getCountryCode()
    # for code, name in COUNTRIES.items():
    #     # print(code+""+name)
    #     if name == country_name:
    #         return code
    if country_name in all_code.keys():
        return all_code[country_name]
    else:
        return None

sh = shelve.open('movie_region.dat', 'c')
dic = sh["region"]
sh.close()

cc_movie_number = {}
for key in dic.index:
        country_name = key
        # print(country_name)
        movie_number = dic[key]
        code = get_country_code(country_name)
        # print(code)
        if code:
            cc_movie_number[code] = movie_number

# 为了使颜色分层更加明显
cc_level_1, cc_level_2, cc_level_3,cc_level_4,cc_level_5,cc_level_6,cc_level_7 = {}, {}, {},{}, {}, {},{}
for cc,number1 in cc_movie_number.items():
    if number1>3000:
        cc_level_7[cc] = number1
    elif number1<3000 and number1>2000:
        cc_level_6[cc] = number1
    elif number1<2000 and number1>900:
        cc_level_5[cc] = number1
    elif number1<900 and number1>675:
        cc_level_4[cc] = number1
    elif number1<675 and number1>450:
        cc_level_3[cc] = number1
    elif number1<450 and number1>225:
        cc_level_2[cc] = number1
    else:
        cc_level_1[cc] = number1

wm_style = RotateStyle(color='#fde0dc',base_style=LightColorizedStyle)
world = World(style=wm_style)
world.title = '近10年世界范围各个地区的电影数量'
world.add('不足225部', cc_level_1)
world.add('225——450部', cc_level_2)
world.add('450——675部', cc_level_3)
world.add('675——900部', cc_level_4)
world.add('900——2000部', cc_level_5)
world.add('2000——3000部', cc_level_6)
world.add('超过3000部', cc_level_7)

world.render_to_file('近10年世界范围各个地区的电影数量.svg')
