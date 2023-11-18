import json
import os
import re
import time

import requests
import subprocess

from lxml import etree

if not os.path.exists('./music'):
    os.mkdir('./music')


class WangYiYun:
    def __init__(self):  # 初始化headers和parms参数以及接口
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            'Referer': 'https://music.163.com/'
        }
        self.params = {
            "csrf_token": ""
        }
        self.post_url = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token="
        self.get_page_url = "https://music.163.com/discover/toplist"

    def get_key(self, ids):  # 根据ids获取key参数，返回字典
        d1 = '{"ids":"[%s]","level":"standard","encodeType":"aac","csrf_token":""}' % ids
        res = subprocess.run(["D:/nodeJs/node.exe", '网易云.js', 'main123', d1], capture_output=True, text=True,
                             shell=True)
        data = res.stdout.strip().replace('params', '"params"').replace('encSecKey', '"encSecKey"').replace("'", '"')
        data_dict = json.loads(data)
        return data_dict

    """
    获取url，传入url和方法，如果是post请求则还需传入一个ids参数，并对接口URL进行请求，
    返回包含音频地址的json文件
    如果请求为GET请求，则直接获取音乐界面，返回text数据
    """

    def get_url(self, url, method, **kwargs):
        if method == 'POST':
            response = requests.post(url=url,
                                     headers=self.headers,
                                     params=self.params,
                                     data=self.get_key(ids=kwargs['ids'])).json()
            return response
        elif method == 'GET':
            response = requests.get(url=url,
                                    headers=self.headers)
        else:
            response = False
        return response

    """
    以传入的音乐名称为文件名，写入到music文件夹中，以m4a为后缀名，如果存在则返回Fasle
    """

    def write_data(self, content, music_name):
        music_name = re.sub(r'[?\\/*"<>|]', '', music_name)
        music_location = f"./music/{music_name}.m4a"
        if not os.path.exists(music_location):
            with open(music_location, 'wb') as fp:
                fp.write(content)
            print(f"{music_name}下载完成！！")
        else:
            print(f"{music_name}已经存在： {music_location}")
            return False

    """
    解析数据，如果传入的方法为POST，说明传入的数据是包含音乐URL的json字符串，则提取音乐URL并返回该URL
    如果传入的方法为GET，说明传入的是页面，则解析出音乐名称和音乐ids，并压缩为字典，返回字典
    """

    def parse_data(self, data, method):
        if method == 'POST':
            music_url = data['data'][0]['url']
            content = self.get_url(music_url, "GET")
            if content:
                return content
            else:
                print("音乐请求失败！")

        elif method == "GET":
            tree = etree.HTML(data.text)
            music_list = tree.xpath("//ul[@class='f-hide']/li/a/@href")
            name_list = tree.xpath("//ul[@class='f-hide']/li/a/text()")
            ids_list = [i.strip('/song?id=') for i in music_list]
            item_dict = dict(zip(name_list, ids_list))
            return item_dict

    """
    执行函数，如果传入的方法为GET，说明传入的数据是页面URL，则对该URL进行请求，并调用解析函数返回包含音乐名称和ids的字典
    如果传入的方法为POST，说明传入的数据是音乐URL，则通过获取函数获取到音乐的二进制流，返回音乐二进制流
    """

    def execute_function(self, url, method, **kwargs):
        if method == "GET":
            page = self.get_url(url, method="GET")
            if page:
                item_dict = self.parse_data(page, "GET")
                return item_dict  # 返回音乐名称和其ids
            else:
                print("页面解析错误")

        elif method == 'POST':
            music_data = self.get_url(url=url, method='POST', ids=kwargs['ids'])
            if music_data:
                content = self.parse_data(data=music_data, method='POST').content
                return content  # 返回音频数据
            else:
                return False

    """
    主函数，调控整个函数
    """

    def run(self):
        item_dict = self.execute_function(self.get_page_url, method='GET')
        for music_name, ids in item_dict.items():
            try:
                content = self.execute_function(self.post_url, method='POST', ids=ids)
            except Exception as e:
                content = False
                print(f"《{music_name}》为会员专享，请登录获取csrf_token参数！")
            finally:
                if content:
                    self.write_data(content, music_name)
            time.sleep(1)
        print("全部下载已完成！")

# TODO
if __name__ == '__main__':
    wyy = WangYiYun()
    wyy.run()
