# coding:utf-8

import pygame
import time
import pymysql


class MusicPlay:
    def __init__(self):
        self.connet_mysql = None
        self.cursor = None

    def play_music(self):
        filepath = self.music_path
        pygame.mixer.init()
        # 加载音乐
        pygame.mixer.music.load(filepath)
        print("Start play %s music %s" % (self.music_author, self.music_name))
        pygame.mixer.music.play(start=0.0)
        lyric_list = self.music_lyric.split(',')
        cust_time = 0
        for lyric in lyric_list:
            time.sleep(2)
            cust_time = cust_time + 2
            print(lyric)
        print(cust_time)
        music_time = time.strptime(self.music_time, "%M:%S")
        print(music_time.tm_min * 60 + music_time.tm_sec)
        time.sleep(music_time.tm_min * 60 + music_time.tm_sec + 3 - cust_time)
        pygame.mixer.music.stop()
        print("Current one music end, start play next one music!")

    def get_music(self):
        self.cursor.execute("select * from musicdata.kwmusic")
        self.music_data = self.cursor.fetchall()
        for music in (self.music_data):
            # print(music)
            self.music_name = music[1]
            self.music_author = music[2]
            self.music_time = music[8]
            self.music_path = music[11]
            self.music_lyric = music[12]
            self.play_music()

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
        self.connect_mysql()
        self.get_music()
        self.cursor.close()
        self.connet_mysql.close()

if __name__ == '__main__':
    MusicPlay = MusicPlay()
    MusicPlay.run()
