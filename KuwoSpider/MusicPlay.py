# coding:utf-8

import pygame
import time
import pymysql


class MusicPlay:
    def __init__(self):
        self.connet_mysql = None
        self.cursor = None
        self.total = 0
        self.lyric_list =[]

    def play_music(self):
        filepath = self.music_path
        pygame.mixer.init()
        # 加载音乐
        pygame.mixer.music.load(filepath)
        print("Start play %s music %s" % (self.music_author, self.music_name))
        print("剩余 %s 歌"%self.total)
        pygame.mixer.music.play(start=0.0)
        music_time = time.strptime(self.music_time, "%M:%S")
        music_total_time = music_time.tm_min * 60 + music_time.tm_sec
        print("歌曲时长",music_total_time,"秒")
        cust_time = 0
        total_time = 0
        for lyric in self.music_lyric:
            slep_time = float(lyric['time'])-cust_time
            time.sleep(slep_time)
            print(lyric['lineLyric'])
            cust_time = float(lyric['time'])
            total_time=total_time+slep_time
        # print(total_time)
        time.sleep(music_time.tm_min * 60 + music_time.tm_sec + 2 - total_time)
        pygame.mixer.music.stop()
        print("Current one music end, start play next one music!")

    def get_music(self):
        self.cursor.execute("select * from musicdata.kwmusic")
        self.music_data = self.cursor.fetchall()
        total = len(self.music_data)
        print("共 %s 首歌即将播放"%total)
        for music in (self.music_data):
            # print(music)
            self.total = total -1
            self.music_name = music[1]
            self.music_author = music[2]
            self.music_time = music[9]
            self.music_path = music[12]
            print(self.music_path)
            self.music_lyric = eval(music[13])
            # print(self.music_lyric)
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
