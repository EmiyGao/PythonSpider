import newspaper
from newspaper import Article
import os
import threading
from queue import Queue
import json
import time


class NewsSpider:

    def __init__(self):
        self.current_path = os.path.dirname(__file__)
        self.main_url_file = 'platform list.txt'
        self.file_path = os.path.join(self.current_path, self.main_url_file)
        self.news_paper_size = None
        self.news_brand = None
        self.Article_detas_list = None

        self.article_url_queue = Queue()
#        self.content_queue = Queue()

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
            news_paper = newspaper.build(platfrom_url)
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
        while True:
            article_url = self.article_url_queue.get()
            print(article_url[1])
            print("sleep 3 secs")
            time.sleep(3)
            Article_html = Article(url=article_url[1])
            try:
                Article_html.download()
            except:
                print("error in url",Article_html)
                continue
            else:
                Article_html.parse()
#                self.Article_detas_list = []
                Article_details = {}
                Article_details["class"] = article_url[0]
                Article_details["title"] = Article_html.title if len(Article_html.title) > 0 else None
                Article_details["top_image"] = Article_html.top_image if len(Article_html.top_image) > 0 else None
                Article_details["author"] = Article_html.authors if len(Article_html.authors) > 0 else None
                Article_details["Image list"] = Article_html.images if len(Article_html.images) > 0 else None
                Article_details["Videos"] = Article_html.movies if len(Article_html.movies) > 0 else None
                Article_details["Text"] = Article_html.text if len(Article_html.text) > 0 else None
                if Article_details["Text"] and Article_details["title"] is not None:
                    Article_html.nlp()
                    Article_details["summary"] = Article_html.summary if len(Article_html.summary) > 0 else None
                    Article_details["keywords"] = Article_html.keywords if len(Article_html.keywords) > 0 else None
                else:
                    Article_details["summary"] = None
                    Article_details["keywords"] = None
#                self.Article_detas_list.append(Article_details)
                print(Article_details)
                self.save_data(Article_details)
                self.article_url_queue.task_done()
        print("*******end of get parse_article*********")




    # save article data
    def save_data(self,Article_detas):
        print("*******start save_data*********")
        file_path = os.path.join(self.current_path ,'news details.txt')
        with open(file_path, "a", encoding="utf-8") as pf:
#            for content in Article_detas_list:
                details = str(Article_detas)
                pf.write(json.dumps(details, ensure_ascii=False, indent=1))
                pf.write("\n")
                print("saved successfully")

    # main logic:
    def run(self):
        self.url_path()
        # 1. prepare url list for different platform
        plat_url_list = self.platform_url_list()
        # 2. according to the different platform to get all the articles url
        self.articles_url_list(plat_url_list)
        # 3. parse url and get article details and parse it.
        self.parse_article()
        # 4. save article details
        # 5. start main thread
        # for t in thread_list:
        #     t.setDaemon(True)  # when main thread end, program end, no need to check child thread completed or not
        #     t.start()
        #print("main thread end")
        # 6. hold main thread untill all the Child thread completed
        # for q in [self.article_url_queue]:
        #     q.join()
        # print("all thread end")


if __name__ == '__main__':
    NewsSpider = NewsSpider()
    NewsSpider.run()
