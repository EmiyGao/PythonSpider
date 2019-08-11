import newspaper
from newspaper import Article
import os
from queue import Queue
import json
import time
from fake_useragent import UserAgent
import telnetlib
import random
import requests
import pymysql


class NewsSpider:

    def __init__(self):
        self.current_path = os.path.dirname(__file__)
        self.main_url_file = 'platform list.txt'
        self.file_path = os.path.join(self.current_path, self.main_url_file)
        self.news_paper_size = None
        self.news_brand = None
        self.Article_detas_list = None
        self.user_agent_list  = None
        self.ip_address_list = None
        self.Article_details = {}
        self.connet_mysql = None
        self.cursor_db = None
        self.article_url_queue = Queue()

    # # if platform list.txt is empty, get populate url list and write into the file
    def url_path(self):
        if os.path.getsize(self.file_path) == 0:
            with open(self.file_path, "w+", encoding="utf-8") as uf:
                popular_urls_list= newspaper.popular_urls()
                for i in range(len(popular_urls_list)):
                    uf.write(popular_urls_list[i])
                    uf.write("\n")
            print("populate url list have worte")

    # get different platform url
    def platform_url_list(self):
        platform_list = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                print(line)
                platform_list.append(line)
            print(platform_list)
        return platform_list
        print("*******end of get platform_url*********")
    # build source and get articles urls

    def articles_url_list(self,plat_url_list):
        print("*******start get articles_url*********")
        for platfrom_url in plat_url_list:
            news_paper = newspaper.build(platfrom_url,memoize_articles=False)   #got all
#            news_paper = newspaper.build(platfrom_url)    # got from start
            for article in news_paper.articles:
                article_list = []
                self.news_brand = news_paper.brand
                article_list.append(self.news_brand)
                article_list.append(article.url)
                print(article_list)
                self.article_url_queue.put(article_list)
            print("have got", self.news_brand, news_paper.size(), "articles'")
        print("*******end of get articles_url*********")

    # download articles and parse
    def parse_article(self):
        print("*******start of parse article*********")
        self.user_agent_list = self.User_Agent()
#        self.ip_address_list = self.get_ip_address()
        self.connect_mysql()
        while not self.article_url_queue.empty():
            article_url = self.article_url_queue.get()
            print(article_url[1])
            verfity_result = self.verfity_art_url(article_url[1])
            if verfity_result == 200:
                print("sleep 3 secs")
                time.sleep(3)
                Article_html = Article(url=article_url[1])
                try:
                    Article_html.download()
                except Exception:
                    print("error in url",Article_html)
                    continue
                else:
                    Article_html.parse()
                    self.Article_details = {}
                    self.Article_details["class"] = article_url[0]
                    self.Article_details["title"] = Article_html.title if len(Article_html.title) > 0 else ' '
                    self.Article_details["top_image"] = Article_html.top_image if len(Article_html.top_image) > 0 else ' '
                    self.Article_details["author"] = Article_html.authors if len(Article_html.authors) > 0 else ' '
                    self.Article_details["Image_list"] = Article_html.images if len(Article_html.images) > 0 else ' '
                    self.Article_details["Videos"] = Article_html.movies if len(Article_html.movies) > 0 else ' '
                    self.Article_details["Text"] = Article_html.text if len(Article_html.text) > 0 else ' '
                    if self.Article_details["Text"] and self.Article_details["title"] is not ' ':
                        Article_html.nlp()
                        self.Article_details["summary"] = Article_html.summary if len(Article_html.summary) > 0 else ' '
                        self.Article_details["keywords"] = Article_html.keywords if len(Article_html.keywords) > 0 else ' '
                    else:
                        self.Article_details["summary"] = ' '
                        self.Article_details["keywords"] = ' '
                    print(self.Article_details)
#                    self.save_data(Article_details)
                    self.save_into_db()
            else:
                print("invalid article, pass")
            self.article_url_queue.task_done()
        print("*******end of get parse_article*********")

    def User_Agent(self):
        ua = UserAgent(verify_ssl=False)
        print("got UserAgent")
        return ua

    def verfity_art_url(self,article_url):
        user_agent = self.user_agent_list.random
        headers = {"user-agent":user_agent}
        print(headers)
        url = article_url
        response = requests.get(url=url, headers=headers, timeout=5)
        print(response.status_code)
        return response.status_code

    def connect_mysql(self):
        self.connet_mysql = pymysql.connect(host='127.0.0.1',
                                      user='root',
                                      password ='18091495112',
                                      db ='newsdata',
                                      port = 3306,
                                      charset='utf8')
        self.cursor = self.connet_mysql.cursor()
        print("connected to MySQL DB")

    # save article data, use mysqldb to repleace txt
#     def save_data(self,Article_detas):
#         print("*******start save_data*********")
#         file_path = os.path.join(self.current_path ,'news details.txt')
#         with open(file_path, "a", encoding="utf-8") as pf:
# #            for content in Article_detas_list:
#                 details = str(Article_detas)
#                 pf.write(json.dumps(details, ensure_ascii=False, indent=1))
#                 pf.write("\n")
#                 print("saved successfully")

    def save_into_db(self):
        sql = 'insert into news_content(news_platform,news_title,news_top_image_url,news_author,news_image_list,news_videos,news_text,news_summary,news_keywords) values("%s","%s","%s","%s","%s","%s","%s","%s","%s")' \
              %(pymysql.escape_string(self.Article_details["class"]),
                pymysql.escape_string(self.Article_details["title"]),
                pymysql.escape_string(self.Article_details["top_image"]),
                self.Article_details["author"],
                self.Article_details["Image_list"],
                pymysql.escape_string(self.Article_details["Videos"]),
                pymysql.escape_string(self.Article_details["Text"]),
                pymysql.escape_string(self.Article_details["summary"]),
                self.Article_details["keywords"])
        print(sql)
        try:
            self.cursor.execute(sql)
            self.connet_mysql.commit()
        except:
            print("*****************************error at sql %s while save data into DB" %sql)

    # main logic:
    def run(self):
        self.url_path()
        # 1. prepare url list for different platform
        plat_url_list = self.platform_url_list()
        # 2. according to the different platform to get all the articles url
        self.articles_url_list(plat_url_list)
        # 3. parse url and get article details and parse it. at last save article details into DB
        self.parse_article()
        # 4. close DB
        self.cursor.close()
        self.connet_mysql.close()

if __name__ == '__main__':
    NewsSpider = NewsSpider()
    NewsSpider.run()
