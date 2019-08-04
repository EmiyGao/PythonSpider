import requests
from lxml import etree
import json
import threading
from queue import Queue

class CNNSpider:
# init program and defiend parmets
    def __init__(self):
        # main url, will rebuild at prepare_url_list
        self.start_url = 'https://edition.cnn.com/{}'
        self.apart_url = 'https://edition.cnn.com'
        self.headers = {
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}
        self.headers2 = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36"}
        # news class, like 'world', 'politics', 'business' etc.
        self.news_class = None
        self.news_type_list = [' ', 'world', 'politics', 'business', 'health', 'entertainment', 'sport']
        self.xpath_zone = None
        # defined Queue for Thread process.
        self.main_url_queue = Queue()
        self.html_queue= Queue()
        self.content_queue = Queue()

# prepare main url list
    def prepare_url_list(self):
        for i in range(len(self.news_type_list)):
            main_url_list = []
            self.news_class = self.news_type_list[i]
            print("news class is:", self.news_class)
            if self.news_class is None:
                main_url_list.append('CNN main page')
            else:
                main_url_list.append(self.news_class)
            main_url = self.start_url.format(self.news_class)
            print("main url is:", main_url)
            main_url_list.append(main_url)
            if self.news_class == ' ':
                self.xpath_zone = 'intl_homepage1-zone'

            if self.news_class in ['world', 'politics', 'health', 'entertainment', 'sport', ]:
                self.xpath_zone = self.news_class + '-zone'

            if self.news_class == 'business':
                self.xpath_zone = 'us-zone'
            main_url_list.append(self.xpath_zone)

# put main url into Queue
            self.main_url_queue.put(main_url_list)

# parse details page url
    def parse_details_url(self, details_url):
        response = requests.get(url=details_url, headers=self.headers2)
        return response.content.decode()

# parse main url
    def parse_url(self):
        while True:
# get main url from main url Queue
            fm_q_url = self.main_url_queue.get()
            url = fm_q_url[1]
            response = requests.get(url=url, headers=self.headers)
            print("*********parse url successfully**********")
            print(response.status_code)
# put decode resonse html into html_queue
            con_tent = []
            con_tent.append(fm_q_url[0])
            con_tent.append(response.content.decode('utf-8'))
            con_tent.append(fm_q_url[2])
            self.html_queue.put(con_tent)
# get from main_url_queue task completed
            self.main_url_queue.task_done()

# decode html and get html_str to get hetml page detaisl
    def get_content_list(self):
        while True:
            html_q_str = self.html_queue.get()
            html_str = html_q_str[1]
            xpath_zone = html_q_str[2]
            html = etree.HTML(html_str)
            print(html)
            print("title is", html.xpath("//*[contains(@id,'" + xpath_zone + "')]//li//h3"))
            div_list = html.xpath("//*[contains(@id,'" + xpath_zone + "')]//li//h3")
            print("*****div_list******", div_list)
            content_list = []
            for div in div_list:
                item = {}
                print(div)
                print(div.attrib, div.text)
                print(div.xpath("./a/span[1]/text()"))
                item["class"] = html_q_str[0]
                item["title"] = div.xpath("./a/span[1]/text()")[0] if len(
                    div.xpath(".//span[@class = 'cd__headline-text']/text()")) > 0 else None
                # item["title_pic"] = self.start_url+ div.xpath(".//div[@class='media']/a/img/@src")[0] if len(div.xpath(".//div[@class='media']/a/img/@src")) > 0 else None
                # print(div.xpath(".//div[@class='media']/a/img/@src"))
                item["title_url"] = self.apart_url + div.xpath("./a/@href")[0] if len(div.xpath("./a/@href")) > 0 else None
                print(self.apart_url + div.xpath("./a/@href")[0])
                if item["title"] and item["title_url"] is not None:
                    item["details"] = self.get_details_page(item["title_url"])
                    content_list.append(item)
                    print(content_list)

            self.content_queue.put(content_list)
            self.html_queue.task_done()

# get title detials and detials page contents
    def get_details_page(self, title_url):
        details_html_str = self.parse_details_url(title_url)
        details_html = etree.HTML(details_html_str)
        print(details_html)
        print(details_html.attrib, details_html.text)
        details_page_list = []
        details = {}
# get title contents
        print("title", details_html.xpath("//article//h1/text()"))
        details["det_title"] = details_html.xpath("//article//h1/text()")[0] if len(
            details_html.xpath("//article//h1/text()")) > 0 else None
        print("authority is :", details_html.xpath("//article//p[1]/span/text()"))
        details["dta_author"] = details_html.xpath("//article//p[1]/span/text()") if len(
            details_html.xpath("//article//p[1]/span/text()")) > 0 else None
        print("datetime is :", details_html.xpath("//article//p[3]/text()"))
        details["datetime"] = details_html.xpath("//article//p[3]/text()") if len(
            details_html.xpath("//article//p[3]/text()")) > 0 else None
        print("title is", details_html.xpath("//*[@id='body-text']/div[1]//p/text()"))
        details["CNN_title"] = details_html.xpath("//*[@id='body-text']/div[1]//p/text()")[0] if len(
            details_html.xpath("//*[@id='body-text']/div[1]//p/text()")) > 0 else None
# detials page contents
        print("details list is:", details_html.xpath("//*[@id='body-text']/div[1]"))
        det_div_list = details_html.xpath("//*[@id='body-text']/div[1]")
        det_details = []
        for det_div in det_div_list:
            details_list = det_div.xpath(".//div[contains(@class, 'paragraph')]//text()")
            det_details.extend(details_list)
        details["details"] = det_details
        details_page_list.append(details)
        print(details_page_list)
        return details_page_list

# save data into text file with class name
    def save_data(self):
        file_path = 'CNN.txt'
        with open(file_path, "w", encoding="utf-8") as f:
            while True:
                content_list = self.content_queue.get()
                for content in content_list:
                    f.write(json.dumps(content, ensure_ascii=False, indent=1))
                    f.write("\n")
                self.content_queue.task_done()
                print("saved successfully")

# program main logic
    def run(self):
        thread_list = []
        # 1. get start url and prepare url list for (world,politics,business,health,entertainment,"style","travel",sport,videos)
        # give 5 Thread to proces, and save the result into Queue
        for i in range(5):
            t_url = threading.Thread(target=self.prepare_url_list)
            thread_list.append(t_url)
        # 2.  give 10 Thread to parse url and get response html save into Queue
        for i in range(10):
            t_parse = threading.Thread(target=self.parse_url)
            thread_list.append(t_parse)
        # 3. give 20 Thread to parse detals url and parse deitals
        for i in range(20):
            t_html = threading.Thread(target=self.get_content_list)
            thread_list.append(t_html)
        # 4. give 5 Thread to save data
        for i in range(5):
            t_save = threading.Thread(target=self.save_data)
            thread_list.append(t_save)
        # 5. start main thread, and when main thread end, program end, no need to check child thread completed or not
        for t in thread_list:
            t.setDaemon(True)   #when main thread end, program end, no need to check child thread completed or not
            t.start()
        print("main thread end")
        # 6. hold main thread untill all the Child thread completed
        for q in [self.main_url_queue, self.html_queue, self.content_queue]:
            q.join()
        print("all thread end")

# main process logic
if __name__ == '__main__':
    CNNSpider = CNNSpider()
    CNNSpider.run()
