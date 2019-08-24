# coding:utf-8
from queue import Queue
import threading
import time
from fake_useragent import UserAgent
import random
import requests
import json
import pymysql
import os

class KuwoMusicSpider:

    def __init__(self):
        self.start_url = 'http://www.kuwo.cn/api/www/bang/bang/musicList?bangId={}'
        self.get_mp3_url = "http://www.kuwo.cn/url?format=mp3&rid={}&response=url&type=convert_url3&br=128kmp3"
        self.lyric_url = "http://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId={}"
        self.url_list = None
        self.user_agent_list = None
        self.music_mp3 =None
        self.music_data =None
        self.Article_details = {}
        self.url_queue = Queue()
        self.html_queue = Queue()
        self.music_queue = Queue()
        self.music_details_queue = Queue()

    def User_Agent(self):
        ua = UserAgent(verify_ssl=False)
        print("got UserAgent")
        return ua

    def get_url_list(self):
        apart_url = '&pn={}&rn=30'
        # for i in range(158, 159):   #类型数字
        for i in range(93, 94):
            a = self.start_url.format(i)
            for j in range(1, 3):  #page
                self.url_list = a + apart_url.format(j)
                # print(self.url_list)
                self.url_queue.put(self.url_list)

    def parse_url(self):
        while not self.url_queue.empty():
            url = self.url_queue.get()
            print(url)
            user_agent = self.user_agent_list.random
            headers = {"user-agent": user_agent}
            print(headers)
            response = requests.get(url=url, headers=headers, timeout=3)
            print("*********parse url successfully**********")
            if response.status_code == 200:
                self.html_queue.put(response.json())
            self.url_queue.task_done()

    def get_audio_list(self):
        while not self.html_queue.empty():
            html_str = self.html_queue.get()
            music_list = html_str.get('data')
            if len(music_list) == 0:
                print("it empty url")
                continue
            else:
                for music in music_list.get('musicList'):
                    print(music)
                    self.music_queue.put(music)
            self.html_queue.task_done()

    def parse_music(self):
        print("start parse_music")
        while not self.music_queue.empty():
            music_details = self.music_queue.get()
            self.music_details = {}
            self.music_details["歌手"] = music_details['artist']
            self.music_details["图片"] = music_details['pic']
            self.music_details["排序变化"] = music_details['rank_change']
            self.music_details["是否有MV"] = music_details['hasmv']
            self.music_details["专辑图片"] = music_details['albumpic']
            self.music_details["发布日期"] = music_details['releaseDate']
            self.music_details["专辑"] = music_details['album']
            self.music_details["歌曲时间"] = music_details['songTimeMinutes']
            self.music_details["歌曲名字"] = music_details['name']
            self.music_details["rid"] = music_details['rid']
            self.music_details["mp3_url"],self.music_mp3 = self.get_music(self.music_details["rid"])
            self.music_details["歌词"] = self.get_lyric(self.music_details["rid"])
            if self.music_details["mp3_url"] is not None:
                self.music_details_queue.put(self.music_details)
                self.save_mp3(self.music_mp3)
                self.save_into_db()
            print(self.music_details)
            self.music_queue.task_done()

    def get_music(self, rid):
        details_mp3_url = self.get_mp3_url.format(rid)
        mp3_user_agent = self.user_agent_list.random
        headers = {"user-agent": mp3_user_agent}
        print(headers)
        response = requests.get(url=details_mp3_url, headers=headers, timeout=3)
        if response.status_code == 200:
            mp3_url = response.json().get('url')
            response1 = requests.get(url=mp3_url, headers=headers, timeout=3)
            if response1.status_code == 200:
                self.music_data = response1.content
            else:
                mp3_url = None
        else:
            mp3_url = None
        return mp3_url,self.music_data

    def get_lyric(self, rid):
        details_lyric_url = self.lyric_url.format(rid)
        lyric_user_agent = self.user_agent_list.random
        headers = {"user-agent": lyric_user_agent}
        print(headers)
        response = requests.get(url=details_lyric_url, headers=headers, timeout=3)
        if response.status_code == 200:
            lyric_str = response.json().get('data').get('lrclist')
        #     lyric_list = []
        #     for lyric in lyric_str:
        #         lyric_list.append(lyric.get('lineLyric'))
        # else:
        #     lyric_list = None
        return lyric_str

    def save_into_db(self):
        sql = 'insert ignore into musicdata.kwmusic(music_name,music_author,music_key,music_picture,music_rank,music_hasmv,music_album,music_albumpic,music_time,music_releaseDate,music_mp3_url,music_path,music_lyric) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'\
              % (pymysql.escape_string(self.music_details["歌曲名字"]),
                     pymysql.escape_string(self.music_details["歌手"]),
                    pymysql.escape_string(self.music_details["歌曲名字"]+'-'+self.music_details["歌手"]),
                     pymysql.escape_string(self.music_details["图片"]),
                     pymysql.escape_string(self.music_details["排序变化"]),
                     self.music_details["是否有MV"],
                     pymysql.escape_string(self.music_details["专辑"]),
                     pymysql.escape_string(self.music_details["专辑图片"]),
                     pymysql.escape_string(self.music_details["歌曲时间"]),
                     pymysql.escape_string(self.music_details["发布日期"]),
                     pymysql.escape_string(self.music_details["mp3_url"]),
                     pymysql.escape_string("F:\\PythonMusic\\{}+{}.mp3".format(self.music_details["歌曲名字"], self.music_details["歌手"])),
                     self.music_details["歌词"])


        print(sql)
        try:
            self.cursor.execute(sql)
            self.connet_mysql.commit()
        except:
            print("*****************************error at sql %s while save data into DB" % sql)

    def save_data(self):
        file_path = "音乐.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            while not self.music_details_queue.empty():
                music_list = self.music_details_queue.get()
                f.write(json.dumps(music_list, ensure_ascii=False, indent=1))
                f.write("\n")
                self.music_details_queue.task_done()
                print("saved successfully")

    def save_mp3(self,mp3):
        file_path = "F:\\PythonMusic\\{}+{}.mp3"
        if os.path.exists(file_path) is False:
            print("正在下载第", self.music_details["歌曲名字"], "歌曲")
            with open(file_path.format(self.music_details["歌曲名字"], self.music_details["歌手"]),"wb") as mf:
                mf.write(mp3)

    def connect_mysql(self):
        self.connet_mysql = pymysql.connect(host='127.0.0.1',
                                            user='root',
                                            password='18091495112',
                                            db='newsdata',
                                            port=3306,
                                            charset='utf8mb4')
        self.cursor = self.connet_mysql.cursor()
        print("connected to MySQL DB")

    def run(self):
        thread_list = []
        self.connect_mysql()
        self.user_agent_list = self.User_Agent()
        for i in range(5):
            t_get_url = threading.Thread(target=self.get_url_list)
            thread_list.append(t_get_url)
        time.sleep(3)
        for i in range(5):
            t_parse_url = threading.Thread(target=self.parse_url)
            thread_list.append(t_parse_url)

        for i in range(5):
            t_audio_list = threading.Thread(target=self.get_audio_list)
            thread_list.append(t_audio_list)

        for i in range(5):
            t_parse_music = threading.Thread(target=self.parse_music)
            thread_list.append(t_parse_music)

        # for i in range(5):
        #     t_save_data = threading.Thread(target=self.save_data)
        #     thread_list.append(t_save_data)

        for t in thread_list:
            t.setDaemon(True)  # main thread end, program end, no need to check child thread completed or not
            t.start()
            t.join()
        print("main thread end")

        self.save_data()
        # for q in [self.url_queue, self.html_queue, self.music_queue]:
        #     q.join()
        # print("all thread end")

        self.cursor.close()
        self.connet_mysql.close()


if __name__ == '__main__':
    KuwoMusicSpider = KuwoMusicSpider()
    KuwoMusicSpider.run()
