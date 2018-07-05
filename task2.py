#coding=utf-8
import requests
import pymysql
from bs4 import BeautifulSoup
import re
Base_URL = "https://github.com/login"
Login_URL = "https://github.com/session"
dbname='exper'
user='root'
passwd=''
conn =  pymysql.connect(host='127.0.0.1', port=3306, user=user, passwd=passwd, db=dbname,charset='utf8')
conn.autocommit(1)
cur=conn.cursor()
def get_github_html(url):
    '''
    这里用于获取登录页的html，以及cookie
    :param url: https://github.com/login
    :return: 登录页面的HTML,以及第一次的cooke
    '''
    response = requests.get(url)
    first_cookie = response.cookies.get_dict()
    return response.text,first_cookie



def get_token(html):
    '''
    处理登录后页面的html
    :param html:
    :return: 获取csrftoken
    '''
    soup = BeautifulSoup(html,'lxml')
    res = soup.find("input",attrs={"name":"authenticity_token"})
    token = res["value"]
    return token


def gihub_login(url,token,cookie):
    '''
    这个是用于登录
    :param url: https://github.com/session
    :param token: csrftoken
    :param cookie: 第一次登录时候的cookie
    :return: 返回第一次和第二次合并后的cooke
    '''

    data= {
        "commit": "Sign in",
        "utf8":"✓",
        "authenticity_token":token,
        "login":"1561356244@qq.com",
        "password":"asd856943"
    }
    response = requests.post(url,data=data,cookies=cookie)
    print(response.status_code)
    cookie = response.cookies.get_dict()
    #这里注释的解释一下，是因为之前github是通过将两次的cookie进行合并的
    #现在不用了可以直接获取就行
    # cookie.update(second_cookie)
    return cookie
def user_list():
    query_sql="select id,login from users where flag is null limit 10000"
    cur.execute(query_sql)
    user_res=cur.fetchall()
    return user_res

if __name__ == '__main__':
    html,cookie = get_github_html(Base_URL)
    token = get_token(html)
    cookie = gihub_login(Login_URL,token,cookie)
    user_res=user_list()
    cnt=0
    for user in user_res:
        print(user[1])
        try:
            response = requests.get("https://github.com/%s"%(user[1]),cookies=cookie)
            soup = BeautifulSoup(response.text)
            res=soup.find_all(name='a',attrs={"class":"u-email"})
            insert_sql="insert into user_email(id,login,email) values(%d,\'%s\',\'%s\')"
            update_sql="update users set flag=1 where id=%d"
            cur.execute(insert_sql%(user[0],user[1],res[0].text))
            cur.execute(update_sql%(user[0]))
            cnt+=1
            if cnt%100==0:
                print("handled %d"%(cnt))
        except:
            update_sql = "update users set flag=2 where id=%d"
            cur.execute(update_sql % (user[0]))

