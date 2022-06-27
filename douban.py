import re
import csv      #进行csv操作

import execjs
from bs4 import BeautifulSoup   #网页解析
import requests

headers={
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Microsoft Edge\";v=\"91\", \"Chromium\";v=\"91\"",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48"
}

# get数据请求
def getUrl(url):
    # headers["Referer"] = url
    # headers["Cookie"] = "ll=\"118203\"; bid=wk0ixe6Hn48; __utmz=30149280.1655035613.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmz=223695111.1655035664.1.1.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _vwo_uuid_v2=D188D860FD48F86CBE81A4C4290E37A1A|5a7e202be58f76a5cc5f63aa6a660b15; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1655040526%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.1701518197.1655035613.1655035613.1655040526.2; __utmb=30149280.0.10.1655040526; __utmc=30149280; __utma=223695111.1620680889.1655035664.1655035664.1655040526.2; __utmb=223695111.0.10.1655040526; __utmc=223695111; ap_v=0,6.0; _pk_id.100001.4cf6=0adefdbda6f4df97.1655035664.2.1655043152.1655035731."
    try:
        resp = requests.get(url, headers=headers, timeout = 30)
        resp.raise_for_status()
        # resp.encoding = resp.apparent_encoding  #根据网页编码解析解码
        resp.encoding = "utf-8"
        return resp
    except:
        return None

# 将list中的数据存储到csv文件中
def saveCsv(dictData,name,Tag = False):
    """
    保存的csv文件先用记事本打开，
    然后另存为ANSI编码的文件，
    最后用excel打开即可！！！
    :param dictData: 字典类型数据,[{},{},{}]
    :param name: 保存的文件名
    :return: null
    """
    print("爬取的数据将保存在csv文件中..")
    with open(f'{name}.csv', 'a', encoding='utf-8',newline='') as csvfile:
        fp = csv.DictWriter(csvfile,fieldnames=dictData[0].keys())
        if Tag:
            fp.writeheader()
        try:
            fp.writerows(dictData)
        except Exception as e:
            print(e)

def getFilm(pid="25845392",num = 0,name = "评论",langlang = False):
    """
    获取电影评论
    :param pid: 电影pid
    :param num: 页数，从0开始
    :param name: 保存的文件名
    :param langlang: 是否保存详细评论
    :return: null
    """
    comment_url = f"https://movie.douban.com/subject/{pid}/reviews?start={str(20*num)}"
    comment_resp = getUrl(comment_url).text
    comment_html = BeautifulSoup(comment_resp, "html.parser")
    review_lists = comment_html.find_all("div",class_="main review-item")
    users = []
    for child in review_lists:
        # print(child)
        user = {}
        user["sid"] = re.findall('"main review-item" id="(.*?)"', str(child))[0]
        user["用户名"] = child.find("a", class_="name").text
        user["评论时间"] = child.find("span", class_="main-meta").text
        user["评分"] = re.findall('title="(.*?)"', str(child.find("span", class_="allstar20 main-title-rating")))
        user["短评"] = child.find("h2").text
        user["长评"] = child.find("div", class_="short-content").text.replace("\n", " ").replace("  ", "")
        user["点赞数"] = child.find("a", class_="action-btn down").text.replace("\n", "").replace(" ", "")
        user["反对数"] = child.find("a", class_="action-btn down").text.replace("\n", "").replace(" ", "")
        if langlang:
            user["长评论详情"] = get_xiangqing(user["sid"])
        users.append(user)

        print(user)
    if num == 0:
        saveCsv(users, name,True)
    else:
        saveCsv(users, name, False)


def get_xiangqing(sid):
    url = f"https://movie.douban.com/j/review/{sid}/full"
    resp = getUrl(url).json()
    str_html = resp["html"]
    html = BeautifulSoup(str_html, "html.parser")
    return html.text

def searchDy(name):
    url = "https://search.douban.com/movie/subject_search?search_text="+name
    resp = getUrl(url)
    r = re.search('window.__DATA__ = "([^"]+)"', resp.text).group(1)
    # 导入js
    with open('main.js', 'r', encoding='utf-8') as f:
        decrypt_js = f.read()
    ctx = execjs.compile(decrypt_js)
    data = ctx.call('decrypt', str(r))  # 有问题
    for item in data['payload']['items']:
        print(item)

def main():
    for i in range(50):
        getFilm("26933210",i,"蜘蛛侠评论详情",True)


if __name__ == '__main__':
    main()