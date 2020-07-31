#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import re
import time
import random
import sys
import urllib
import requests
import pickle
from bs4 import BeautifulSoup


# 搜索小说
def search_book(search_book_name):

    try:
        if search_book_name:
            new_search_book_name = urllib.parse.quote(search_book_name)
            search_url = 'https://www.biquge5200.cc/modules/article/search.php?searchkey=' + \
                new_search_book_name
            novel_source = requests.get(search_url).text
            search_soup = BeautifulSoup(novel_source, "lxml")
            search_book_url = search_soup.find("div", id="hotcontent").find_all("td", class_="odd")

            if len(search_book_url) > 0:
                for item in search_book_url:
                    if item.text == search_book_name:
                        book_url = item.find("a").get('href')
                        return book_url

            else:
                print("未找到您要搜索的小说!")

        else:
            print("请输入小说名称")
    except Exception as e:
        print(e)


# 获取小说名称和下面各个章节的url地址
def get_all_chapter_href(search_url):

    try:
        if search_url:
            new_search_url = requests.get(search_url)
            # 通过F12查看笔趣阁小说页面html结构发现meta标签上gbk格式解析的，所以在这里转一下
            new_search_url.encoding = "gbk"
            chapter_soup = BeautifulSoup(new_search_url.text, "lxml")
            chapter_list = chapter_soup.find("div", id="list").find_all("a")
            booktitle = chapter_soup.find("div", id="maininfo").find("div", id="info").find("h1")
            print("正在下载的小说名称是: " + booktitle.text)

            href_list = []
            for a in chapter_list:
                href_list.append(a.get('href'))

            return href_list, booktitle
        else:
            return None, None

    except Exception as e:
        print(e)


# 获取每个章节下的内容并下载到txt
def get_chapter_content(href_list, booktitle, bookpath):
    try:
        global IsDone  # 说明是全局变量
        global AllDownloadNum  # 说明是全局变量
        i = 0
        NewDownloadNum = 0
        ErrorList = ['/', '\\', '*', '?', ':', '"', '|', '（', '）']  # 不规范命名字符合集
        len_href_list = len(href_list)
        if href_list != None and booktitle != None:
            for url in href_list:
                # 跳过已经下载的
                i = i + 1
                if i <= AllDownloadNum:
                    continue

                # 如果连接太过频繁会报错,所以这里用sleep休眠方式
                time.sleep(1 + random.random())
                chapter_url = requests.get(url)
                chapter_url.encoding = "gbk"
                text = chapter_url.text
                content_soup = BeautifulSoup(text, "lxml")
                chaptername = content_soup.find("div", class_="bookname").find("h1")

                # 替换不规范字符
                ChapterNameList = list(chaptername.text)
                for letter in ChapterNameList:
                    if letter in ErrorList:
                        ChapterNameList.remove(letter)
                ChapterNameStr = ''.join(ChapterNameList)
                ChapterNameStr = ChapterNameStr.strip()  # 去除前后空格

                # 下载目录名称（顺序）
                downloadpath = bookpath + "\\" + str(AllDownloadNum) + \
                               '、' + ChapterNameStr + ".txt"
                # 防止重复下载
                if os.path.exists(downloadpath):
                    print("          该章节已下载,名称是:   " + ChapterNameStr)
                    continue

                content = content_soup.find_all("div", id="content")[0].find_all("p")
                # 下载每一章
                with open(downloadpath, 'a', encoding='utf-8') as f:
                    f.write(chaptername.text + "\n\r\r")
                    # 下载打印格式
                    AllDownloadNum = AllDownloadNum + 1  # 总下载数加一
                    NewDownloadNum = NewDownloadNum + 1  # 单轮累计下载加一
                    print("%4d/%d" % (AllDownloadNum, len_href_list), end=' |')
                    print("%3d" % NewDownloadNum, end=' ')
                    print("正在下载的章节名称是: " + ChapterNameStr)
                    for book in content:
                        f.write(book.text + "\n\r")# 写入内容
                
                # 判断全书是否下载完成
                if AllDownloadNum >= len_href_list:
                    print('全书下载完成！')
                    IsDone = True
                
                if NewDownloadNum >= 50: # 每轮50章
                    return
                

        else:
            return

    except Exception as e:
        print(e)

# 创建新的书目录
def creat_newbook_folder(base_path, booktitle):
    if booktitle is None:
        return None
        
    # 读取目录下文件列表
    base_foleder = base_path
    Vname_list = os.listdir(base_foleder)
    print('已下载的小说：')
    for i in Vname_list:
        print('《',i,'》')

    # 指定路径创建新文件夹
    file_path = os.path.join(base_path, booktitle.text)

    if not os.path.exists(file_path):  # 判断文件夹是否已经存在
        os.mkdir(file_path)
        print(file_path + ' 创建成功')
    else:
        print(file_path + ' 目录已存在')

    return file_path

# 记录下载序号
def RecordNum(bookpath):
    # 计算总文件数
    for root, dirs, files in os.walk(bookpath):
        return len(files)

# TODO FillVacancy
'''
# 查漏补缺
def FillVacancy(href_list, booktitle, bookpath):
    # 计算总文件数
    for files in os.walk(bookpath):
        ChapterNameList = files
    ErrorList = ['/', '\\', '*', '?', ':', '"', '|']  # 不规范命名字符合集
    if href_list != None and booktitle != None:
        for url in href_list:
            # 如果连接太过频繁会报错,所以这里用sleep休眠方式
            time.sleep(1 + random.random())
            chapter_url = requests.get(url)
            chapter_url.encoding = "gbk"
            text = chapter_url.text
            content_soup = BeautifulSoup(text, "lxml")
            chaptername = content_soup.find("div", class_="bookname").find("h1")

            # 替换不规范字符
            ChapterNameList = list(chaptername.text)
            for letter in ChapterNameList:
                if letter in ErrorList:
                    ChapterNameList.remove(letter)
            ChapterNameStr = ''.join(ChapterNameList)
            ChapterNameStr = ChapterNameStr.strip()  # 去除前后空格

            downloadpath = bookpath + "\\" + ChapterNameStr + ".txt"
            # 防止重复下载
            if os.path.exists(downloadpath):
                print("该章节已下载,名称是:   " + ChapterNameStr)
                continue

            content = content_soup.find_all("div", id="content")[0].find_all("p")

            # 下载每一章
            with open(downloadpath, 'a', encoding='utf-8') as f:
                f.write(chaptername.text + "\n\r\r")
                # 下载打印格式
                print("正在下载的章节名称是: " + ChapterNameStr)
                for book in content:
                    f.write(book.text + "\n\r")  # 写入内容
'''
    
        
            
# 主函数
if __name__ == "__main__":
    # global
    IsDone = False
    AllDownloadNum = 0
    search_book_name = input("请输入想要下载的小说名称: ")
    while(not IsDone): # 循环
        search_url = search_book(search_book_name)
        href, booktitle = get_all_chapter_href(search_url)
        bookpath = creat_newbook_folder("E:\\book&Paper\\小说\\", booktitle)
        AllDownloadNum = RecordNum(bookpath)
        get_chapter_content(href, booktitle, bookpath)
    # FillVacancy(href, booktitle, bookpath)
