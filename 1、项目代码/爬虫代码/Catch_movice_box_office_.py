# -*- coding: utf-8 -*-
import csv
import socket
import urllib.request
import urllib.error
import urllib.parse
from selenium import webdriver
from time import sleep
import pymysql
from bs4 import BeautifulSoup
import random
import datetime
import requests
import threading
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='yuanye', db='testdb', charset='utf8')
cursor = conn.cursor()
socket.setdefaulttimeout(10)


def catch_movie():
    driver = webdriver.Chrome(
        executable_path='./tools/chromedriver')
    driver.get("http://piaofang.maoyan.com/rankings/year")  # 需要抓取的用户链接，这里注意的是这里的id不是用户的id，而是用户听歌形成的所有时间排行的排行版的id
    movie_year = driver.find_element_by_class_name("select-year ").find_elements_by_css_selector('li')
    create_table()
    movie_year[1].click()
    # title = ["片名", "票房(万元)"]
    # save_movie_info(title)
    sleep(1)
    for i in range(2, len(movie_year)+1):
        try:
            movie_obj = driver.find_element_by_id("ranks-list")
            movies = movie_obj.find_elements_by_tag_name('ul')
            for l in movies:
                movie_name = l.find_element_by_class_name("first-line").text
                movie_money = l.find_element_by_class_name("col2").text
                mysql_save(movie_name, movie_money)
                # movie_info = [movie_name, movie_money]
                # print(movie_info)
                # save_movie_info(movie_info)
            movies.clear()
            print("next page....\n")
            movie_year[i].click()
            sleep(1)
        except Exception as a:
            print(a)
            pass
    driver.quit()


def catch_movie_id():
    driver = webdriver.Chrome(executable_path="./tools/chromedriver")
    my_list = []
    movie_result = mysql_query_movie_name()
    for i in movie_result:
        if i[0] != '':
            my_list.append(i[0])
    create_id_table()  # 存储电影id的表
    while len(my_list) > 0:
        url_catch_id(my_list.pop(), driver)
    driver.quit()


def catch_movie_info():
    movie_info = mysql_query_movie_id()
    my_name_list = []
    my_id_list = []
    for i in movie_info:
        my_name_list.append(i[1])
        my_id_list.append(i[0])
    print(my_name_list)
    print(my_id_list)
    while len(my_name_list) > 0:
        thread = Movie_Thread(my_name_list.pop(), my_id_list.pop())
        thread2 = Movie_Thread(my_name_list.pop(), my_id_list.pop())
        thread.start()
        thread2.start()
        thread.join()
        thread2.join()


def catch_movie_comment_info():
    pass


class Movie_Thread(threading.Thread):
    def __init__(self, movie_name, driver):
        threading.Thread.__init__(self)
        self.movie_name = movie_name
        self.driver = driver

    def run(self):
        # print("开始线程：" + self.name)
        get_one_movie_info(self.movie_name, self.driver)
        print("退出线程：" + self.name)


def url_catch_id(movie_name, driver):
    new_word = urllib.parse.quote(movie_name)
    driver.get('https://movie.douban.com/subject_search?search_text='+new_word+'&cat=1002')
    sleep(1)
    url = driver.find_element_by_xpath("//a[contains(@href,'subject')]")
    movie_id = url.get_attribute("href")
    print("{0}--->{1}".format(movie_name, movie_id))
    mysql_save_id(movie_id[33:-1], movie_name)


def create_table():
    sql = "create table my_movie" \
          "(id INT AUTO_INCREMENT PRIMARY KEY," \
          "movie_key varchar(30)NOT NULL,money_values varchar(18)NOT NULL) " \
          "ENGINE=InnoDB DEFAULT CHARSET=utf8"
    cursor.execute(sql)
    conn.commit()


def create_id_table():
    conn.ping(reconnect=True)
    sql = "create table my_movie_id" \
          "(id INT AUTO_INCREMENT PRIMARY KEY," \
          "movie_id varchar(50)NOT NULL,movie_name varchar(30) NOT NULL)" \
          "ENGINE=InnoDB DEFAULT CHARSET=utf8"
    cursor.execute(sql)
    conn.commit()


def save_movie_info(info):
    with open('movie.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(info)


def mysql_save(movie_name, movie_money):
    conn.ping(reconnect=True)
    try:
        cursor.executemany("insert into my_movie(movie_key,money_values)values(%s,%s)", [(movie_name, movie_money)])
        conn.commit()
    except Exception as a:
        print(a)
        pass


def mysql_save_id(movie_id, movie_name):
    conn.ping(reconnect=True)
    try:
        cursor.executemany("insert into my_movie_id(movie_id,movie_name)values(%s,%s)", [(movie_id, movie_name)])
        conn.commit()
    except Exception as a:
        print(a)
        pass


def mysql_query_movie_name():
    conn.ping(reconnect=True)
    sql = "select movie_key from my_movie;"
    cursor.execute(sql)
    conn.commit()
    result = cursor.fetchall()
    return result


def mysql_query_movie_id():
    conn.ping(reconnect=True)
    sql = "select movie_id,movie_name from my_movie_id;"
    cursor.execute(sql)
    conn.commit()
    result = cursor.fetchall()
    return result


def mysql_query_movie_money(movie_name):
    conn.ping(reconnect=True)
    sql = "select money_values from my_movie where movie_key = '" + movie_name + "';"
    cursor.execute(sql)
    conn.commit()
    result = cursor.fetchall()
    money = 0
    if len(result) > 0:
        for i in result:
            money += int(i[0])
    return str(money)


def getheaders():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 "
        "Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    UserAgent = random.choice(user_agent_list)
    headers = {'User-Agent': UserAgent}
    return headers


def all_replace(movie_synopsis):
    return movie_synopsis.replace('\n', '').replace(' ', '') \
        .replace('　　', '').replace('，', '').replace('(', '').replace(')', '')


def get_one_movie_info(movie_name, movie_id):
    try:
        url = 'https://movie.douban.com/subject/' + movie_id + '/'
        header = getheaders()
        request = urllib.request.Request(url=url, headers=header)
        html = urllib.request.urlopen(request)  # 打开url
        soup = BeautifulSoup(html, "lxml")
        html.close()
        movie_info = soup.find('div', id='info')
        my_info_list = movie_info.text.split("\n")
        director = my_info_list[1][4:]  # 导演
        screenwriter = my_info_list[2][4:]  # 编剧

        movie_sum_money = mysql_query_movie_money(movie_name)  # 电影票房

        starring_people = '无数据'
        starring_list = soup.find('div', id='info').find('span', class_="actor")  # 主演列表
        if starring_list is not None:
            starring_people = starring_list.text[4:]

        movie_type = '无数据'
        movie_type_list = movie_info.find_all('span', property="v:genre")  # 电影类型
        if len(movie_type_list) > 0:
            for i in range(0, len(movie_type_list)):
                movie_type += movie_type_list[i].text + ' '

        production_country = my_info_list[5][9:]  # 制片国家
        if len(production_country) > 5:
            production_country = '非中国大陆'
        elif len(production_country) < 2:
            production_country = '无数据'

        release_date = '无数据'
        release_date_list = movie_info.find('span', property="v:initialReleaseDate")  # 上映时间
        if release_date_list is not None:
            release_date = release_date_list.text

        movie_duration = '无数据'
        movie_duration_flag = movie_info.find('span', property="v:runtime")  # 电影时长
        if movie_duration_flag is not None:
            movie_duration = movie_duration_flag.text

        movie_rating = '无评分'
        movie_rating_flag = soup.find('div', class_="rating_self clearfix")  # 电影评分
        if movie_rating_flag is not None:
            movie_rating = all_replace(movie_rating_flag.text[:4])

        movie_num_people = '无数据'
        movie_num_people_flag = soup.find('div', class_="rating_self clearfix").find('span', property="v:votes")
        if movie_num_people_flag is not None:
            movie_num_people = movie_num_people_flag.text

        movie_similar_ranking = '无数据'  # 同类排行
        movie_similar_ranking_list = soup.find('div', class_="rating_betterthan")
        if movie_similar_ranking_list is not None:
            movie_similar_ranking = ''
            movie_similar_ranking_list = movie_similar_ranking_list.text.replace('  ', '').split("\n")
            for i in movie_similar_ranking_list:
                movie_similar_ranking += i

        movie_synopsis = all_replace(soup.find('div', id="link-report").text)  # 电影简介
        movie_short_comment = all_replace(soup.find('div', class_="mod-hd").find('span', class_="pl").text)  # 短评评论条数
        movie_content = all_replace(
            soup.find('section', class_="reviews mod movie-content").find('span', class_="pl").text)  # 影评条数

        movie_discussion = '无数据'  # 讨论条数
        movie_discussion_flag = soup.find('div', class_="section-discussion").find('p', align="right")
        if movie_discussion_flag is not None:
            movie_discussion = all_replace(movie_discussion_flag.text)

        movie_question = '无数据'  # 问题条数
        movie_question_flag = soup.find('div', id="askmatrix")
        if movie_question_flag is not None:
            movie_question = all_replace(movie_question_flag.find('span', class_="pl").text)

        print(movie_name)  # 影片
        print(director)  # 导演
        print(movie_sum_money + "万元")  # 电影票房
        print(screenwriter)  # 编剧
        print(starring_people)  # 主演
        print(movie_type)  # 电影类型
        print(production_country)  # 制片国家
        print(release_date)  # 上映时间
        print(movie_duration)  # 电影时长
        print(movie_rating)  # 电影评分
        print(movie_num_people)  # 电影评分人数
        print(movie_similar_ranking)  # 同类排行
        print(movie_synopsis)  # 电影简介
        print(movie_short_comment)  # 电影短评
        print(movie_content)  # 影评条数
        print(movie_discussion)  # 讨论条数
        print(movie_question)  # 问题条数
        print('\n')

        sleep(0.5)
    except Exception as a:
        print('\n')
        print("*********************")
        print(a)
        print(movie_name)
        print(movie_id)
        print("*********************")
        print('\n')
        pass


def gettimediff(start, end):
    seconds = (end - start).seconds
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    diff = ("%02d:%02d:%02d" % (h, m, s))
    return diff


def checkip(targeturl, ip):
    headers = getheaders()  # 定制请求头
    proxies = {"http": "http://" + ip, "https": "http://" + ip}  # 代理ip
    try:
        response = requests.get(url=targeturl, proxies=proxies, headers=headers, timeout=5).status_code
        if response == 200:
            return True
        else:
            return False
    except:
        return False


def findip(type, pagenum, targeturl, ip_data):  # ip类型,页码,目标url,存放ip的路径
    list = {'1': 'http://www.xicidaili.com/nt/',  # xicidaili国内普通代理
            '2': 'http://www.xicidaili.com/nn/',  # xicidaili国内高匿代理
            '3': 'http://www.xicidaili.com/wn/',  # xicidaili国内https代理
            '4': 'http://www.xicidaili.com/wt/'}  # xicidaili国外http代理
    url = list[str(type)] + str(pagenum)  # 配置url
    headers = getheaders()  # 定制请求头
    html = requests.get(url=url, headers=headers, timeout=5).text
    soup = BeautifulSoup(html, 'lxml')
    all = soup.find_all('tr', class_='odd')
    for i in all:
        t = i.find_all('td')
        ip = t[1].text + ':' + t[2].text
        is_avail = checkip(targeturl, ip)
        if is_avail == True:
            ip_data.append(ip)
            print(ip)


def getip(targeturl, ip_data):
    start = datetime.datetime.now()  # 开始时间
    threads = []
    for type in range(4):  # 四种类型ip,每种类型取前三页,共12条线程
        for pagenum in range(3):
            t = threading.Thread(target=findip, args=(type + 1, pagenum + 1, targeturl, ip_data))
            threads.append(t)
    print('开始爬取代理ip')
    for s in threads:  # 开启多线程爬取
        s.start()
    for e in threads:  # 等待所有线程结束
        e.join()
    print('爬取完成')
    end = datetime.datetime.now()  # 结束时间
    diff = gettimediff(start, end)  # 计算耗时
    ips = len(ip_data)  # 读取爬到的ip数量
    print('一共爬取代理ip: %s 个,共耗时: %s \n' % (ips, diff))
    print(ip_data)


def get_ip_data():
    ip_data = []
    targeturl = 'https://www.baidu.com/'  # 验证ip有效性的指定url
    getip(targeturl, ip_data)
    return ip_data


if __name__ == '__main__':
    # all_ip_data = get_ip_data() #获取代理ip池,返回all_ip_data列表

    catch_movie()  # 1 电影和票房的关系
    catch_movie_id()  # 2 电影和电影id的关系
    catch_movie_info()  # 3 电影和电影内容信息

