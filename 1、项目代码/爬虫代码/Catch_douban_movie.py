# -*- coding: utf-8 -*-
import random
import urllib.request
import urllib.error
import urllib.parse
import json
from bs4 import BeautifulSoup
import pymysql
from time import sleep
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='yuanye', db='testdb', charset='utf8')
cursor = conn.cursor()


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
    # headers = {'User-Agent': UserAgent}
    return UserAgent


def getipproxy():
    ip_proxy = ['139.129.99.9:3128',
                '122.235.84.116:8118',
                '180.125.137.24:8000',
                '221.225.215.71:8118',
                '118.31.220.3:8080']
    Proxy = random.choice(ip_proxy)
    return Proxy


def all_replace(movie_synopsis):
    return movie_synopsis.replace('\n', '').replace(' ', '') \
        .replace('　　', '').replace('，', '').replace('(', '').replace(')', '')


def get_douban_movie(year):
    try:
        num = 0
        while True:
            url = 'https://movie.douban.com/j/new_search_subjects?sort=T&' \
                  'range=0,10&tags=%E7%94%B5%E5%BD%B1,' + year + '&start=' + str(num)
            proxy = {'http': getipproxy()}
            proxy_support = urllib.request.ProxyHandler(proxy)
            opener = urllib.request.build_opener(proxy_support)
            opener.addheaders = [('User-Agent', getheaders())]
            urllib.request.install_opener(opener)
            html = urllib.request.urlopen(url).read().decode('utf-8')
            json_dict = json.loads(html)
            movie_data = json_dict['data']
            if not movie_data:
                break
            else:
                for i in movie_data:
                    save_douban_movie(i['title'], i['rate'], i['id'], i['url'])
            num += 20
            print(num)
    except Exception as a:
        print(a)
        pass


def get_movie_info(movie_id):
    try:
        url = 'https://movie.douban.com/subject/' + movie_id + '/'
        proxy = {'http': getipproxy()}
        proxy_support = urllib.request.ProxyHandler(proxy)
        opener = urllib.request.build_opener(proxy_support)
        opener.addheaders = [('User-Agent', getheaders())]
        urllib.request.install_opener(opener)
        html = urllib.request.urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(html, "lxml")
        movie_info = soup.find('div', id='info')
        my_info_list = movie_info.text.split("\n")

        movie_name = soup.find('span', property="v:itemreviewed").text
        director = my_info_list[1][4:]  # 导演
        screenwriter = my_info_list[2][4:]  # 编剧
        starring_people = '无数据'
        starring_list = soup.find('div', id='info').find('span', class_="actor")  # 主演列表
        if starring_list is not None:
            starring_people = starring_list.text[4:]

        movie_type = '无数据'
        movie_type_list = movie_info.find_all('span', property="v:genre")  # 电影类型
        if len(movie_type_list) > 0:
            movie_type = ''
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
            release_date = release_date_list.text[:10]

        movie_duration = '无数据'
        movie_duration_flag = movie_info.find('span', property="v:runtime")  # 电影时长
        if movie_duration_flag is not None:
            movie_duration = movie_duration_flag.text

        movie_rating = '无评分'
        movie_rating_flag = soup.find('div', class_="rating_self clearfix")  # 电影评分
        if movie_rating_flag is not None:
            movie_rating = all_replace(movie_rating_flag.text[:4])

        movie_num_people = '无数据'  # 评论人数
        movie_num_people_flag = soup.find('div', class_="rating_self clearfix")
        if movie_num_people_flag is not None and all_replace(movie_num_people_flag.text) != '暂无评分':
            movie_num_people = movie_num_people_flag.find('span', property="v:votes").text

        movie_similar_ranking = '无数据'  # 同类排行
        movie_similar_ranking_list = soup.find('div', class_="rating_betterthan")
        if movie_similar_ranking_list is not None:
            movie_similar_ranking = ''
            movie_similar_ranking_list = movie_similar_ranking_list.text.replace('  ', '').split("\n")
            for i in movie_similar_ranking_list:
                movie_similar_ranking += i

        movie_synopsis = '无数据'  # 电影简介
        movie_synopsis_flag = soup.find('div', id="link-report")
        if movie_synopsis_flag is not None:
            movie_synopsis = all_replace(movie_synopsis_flag.text)

        movie_short_comment = '无数据'  # 短评评论条数
        movie_short_comment_flag = soup.find('div', class_="mod-hd")
        if movie_short_comment_flag is not None:
            movie_short_comment = all_replace(movie_short_comment_flag.find('span', class_="pl").text)

        movie_content = '无数据'  # 影评条数
        movie_content_flag = soup.find('section', class_="reviews mod movie-content")
        if movie_content_flag is not None:
            movie_content = all_replace(movie_content_flag.find('span', class_="pl").text)

        movie_discussion = '无数据'  # 讨论条数
        movie_discussion_flag = soup.find('div', class_="section-discussion")
        if movie_discussion_flag is not None:
            if movie_discussion_flag.find('p', align="right") is not None:
                movie_discussion = all_replace(movie_discussion_flag.find('p', align="right").text)

        movie_question = '无数据'  # 问题条数
        movie_question_flag = soup.find('div', id="askmatrix")
        if movie_question_flag is not None:
            movie_question = all_replace(movie_question_flag.find('span', class_="pl").text)

        movie_all_comment = get_all_comment(movie_id)  # 影片短评

        movie_info_list = [movie_name, movie_id, director, screenwriter, starring_people,
                           movie_type, production_country, release_date, movie_duration,
                           movie_rating, movie_num_people, movie_similar_ranking,
                           movie_synopsis, movie_short_comment, movie_content,
                           movie_discussion, movie_question, movie_all_comment]

        save_movie_info(movie_info_list)
        sleep(0.3)
        print('pass...')
        print('\n')
        # print(movie_name)  # 1影片
        # print(movie_id)  # 2id
        # print(director)  # 3导演
        # print(screenwriter)  # 4编剧
        # print(starring_people)  # 5主演
        # print(movie_type)  # 6电影类型
        # print(production_country)  # 7制片国家
        # print(release_date)  # 8上映时间
        # print(movie_duration)  # 9电影时长
        # print(movie_rating)  # 10电影评分
        # print(movie_num_people)  # 11电影评分人数
        # print(movie_similar_ranking)  # 12同类排行
        # print(movie_synopsis)  # 13电影简介
        # print(movie_short_comment)  # 14电影短评
        # print(movie_content)  # 15影评条数
        # print(movie_discussion)  # 16讨论条数
        # print(movie_question)  # 17问题条数
    except Exception as a:
        print(a)
        print(movie_id)
        pass


def get_all_comment(movie_id):
    url = 'https://movie.douban.com/subject/'+movie_id+'/comments?sort=new_score&status=P'
    proxy = {'http': getipproxy()}
    proxy_support = urllib.request.ProxyHandler(proxy)
    opener = urllib.request.build_opener(proxy_support)
    opener.addheaders = [('User-Agent', getheaders())]
    urllib.request.install_opener(opener)
    html = urllib.request.urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    comment = '无数据'
    comment_flag = soup.find('div', class_="mod-bd")
    if comment is not None:
        comment = ''
        num = 1
        comment_list = comment_flag.find_all('span', class_="short")
        zan_list = comment_flag.find_all('span', class_="votes")
        for i in comment_list:
            comment += "{0}:{1}  {2}赞\n".format(str(num), i.text, zan_list[num-1].text)
            num += 1
    # print(comment)
    return comment


def create_table():
    sql = "create table douban_movie" \
          "(id INT AUTO_INCREMENT PRIMARY KEY," \
          "movie_title varchar(50)NOT NULL," \
          "movie_rate varchar(5)NOT NULL," \
          "movie_id varchar(20)NOT NULL unique," \
          "movie_link varchar(50)NOT NULL unique)" \
          "ENGINE=InnoDB DEFAULT CHARSET=utf8"
    cursor.execute(sql)
    conn.commit()


def create_info_table():
    sql = "create table info_movie" \
          "(id INT AUTO_INCREMENT PRIMARY KEY," \
          "movie_name varchar(100)NOT NULL," \
          "movie_id varchar(15)NOT NULL unique," \
          "director varchar(500)NOT NULL," \
          "screenwriter varchar(500)NOT NULL," \
          "starring_people varchar(500)NOT NULL," \
          "movie_type varchar(18)NOT NULL," \
          "production_country varchar(10)NOT NULL," \
          "release_date varchar(50)NOT NULL," \
          "movie_duration varchar(50)NOT NULL," \
          "movie_rating varchar(8)NOT NULL," \
          "movie_num_people varchar(20)NOT NULL," \
          "movie_similar_ranking varchar(30)NOT NULL," \
          "movie_synopsis varchar(5000)NOT NULL," \
          "movie_short_comment varchar(20)NOT NULL," \
          "movie_content varchar(20)NOT NULL," \
          "movie_discussion varchar(500)NOT NULL," \
          "movie_question varchar(500)NOT NULL," \
          "movie_all_comment varchar(5000)NOT NULL)" \
          "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    cursor.execute(sql)
    conn.commit()


def delete_table():
    sql = 'drop tables douban_movie;'
    cursor.execute(sql)
    conn.commit()


def delete_info_table():
    sql = 'drop tables info_movie;'
    cursor.execute(sql)
    conn.commit()


def query_all_movie_id():
    conn.ping(reconnect=True)
    sql = "select movie_id from douban_movie where movie_id >= '6121039';"
    cursor.execute(sql)
    conn.commit()
    result = cursor.fetchall()
    return result


def save_douban_movie(movie_name, movie_rate, movie_id, movie_link):
    conn.ping(reconnect=True)
    try:
        cursor.executemany("insert into douban_movie(movie_title,movie_rate,movie_id, movie_link)values(%s,%s,%s,%s)"
                           , [(movie_name, movie_rate, movie_id, movie_link)])
        conn.commit()
    except Exception as a:
        print(a)
        pass


def save_movie_info(args):
    conn.ping(reconnect=True)
    try:
        cursor.executemany("insert into info_movie(movie_name,"
                           "movie_id, director, screenwriter, starring_people,"
                           "movie_type, production_country, release_date, movie_duration,"
                           "movie_rating, movie_num_people, movie_similar_ranking,"
                           "movie_synopsis, movie_short_comment, movie_content,"
                           "movie_discussion, movie_question, movie_all_comment"
                           ")values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                           , [(args[0], args[1], args[2], args[3], args[4], args[5], args[6],
                               args[7], args[8], args[9], args[10], args[11], args[12], args[13],
                               args[14], args[15], args[16], args[17])])
        conn.commit()
    except Exception as a:
        print(a)
        print(args[1])
        pass


if __name__ == '__main__':
    delete_table()
    create_table()
    year_list = []
    for i in range(2008, 2019):
        year_list.append(i)
    while len(year_list) > 0:
        year = str(year_list.pop())
        get_douban_movie(year)

    delete_info_table()
    create_info_table()

    movie_id_list = query_all_movie_id()
    for i in movie_id_list:
        get_movie_info(i[0])
