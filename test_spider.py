
import os
import re
import json
import time
import requests
from lxml import etree
from requests import RequestException


class bilibili:
    def __init__(self):
        self.getHtmlHeaders = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q = 0.9",
        }

        self.downloadVideoHeaders = {
            "Referer": "https://www.bilibili.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        }

    # 一般这里得到的网页源码和F12查看看到的不一样，因为F12开发者工具里的源码经过了浏览器的解释
    def getHtml(self, i , url):
        try:
            response = requests.get(url=url, headers=self.getHtmlHeaders)
            if response.status_code == 200:
                return response.text, url, i
        except RequestException:
            print("请求Html错误:")

    def parseHtml(self, html):
        # 用pq解析得到视频标题
        html, url, i = html
        html_obj = etree.HTML(html)
        video_title_ = html_obj.xpath("//title/text()")[0]
        video_title = re.findall(r"(.*?)_哔哩哔哩_bilibili", video_title_)[0]

        # 用正则、json得到视频url;用pq失败后的无奈之举
        pattern = html_obj.xpath(
            '//script[contains(text(), "window.__playinfo__")]/text()'
        )[0]

        video_url = re.findall(r'"video":\[{"id":\d+,"baseUrl":"(.*?)"', pattern)[0]
        audio_url = re.findall(r'"audio":\[{"id":\d+,"baseUrl":"(.*?)"', pattern)[0]

        return {
            "title": video_title,
            "video_url": video_url,
            "audio_url": audio_url,
            "raw_url": url,
            "num": i
        }

    def download_video(self, video):
        title = re.sub(r'[\/:*?"<>|]', "-", video["title"])  # 去掉创建文件时的非法字符
        video_url = video["video_url"]
        audio_url = video["audio_url"]
        url = video["raw_url"]
        num = video["num"]
        title = str(num+1) +"."+ title
        video_filename = title + ".mp4"
        audio_filename = str(num+1)+"."+title + ".mp3"
        headers_ = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            "Referer": url,
        }
        # data_video = requests.get(
        #     video_url, headers=headers_, stream=True, verify=False
        # ).content
        data_audio = requests.get(
            audio_url, headers=headers_, stream=True, verify=False
        ).content

        # with open(video_filename, "wb") as f:
        #     f.write(data_video)

        with open(audio_filename, "wb") as f:
            f.write(data_audio)

        # os.system(
        #     f'ffmpeg -i "{video_filename}" -i "{audio_filename}" -c copy "{title}_merged.mp4"'
        # )
        os.system(f'ffmpeg -i "{audio_filename}" -ar 16000 -ac 1 "{title}.wav"')
        # os.remove(f"{video_filename}")
        os.remove(f"{audio_filename}")

    def run(self, i, url):
        self.download_video(self.parseHtml(self.getHtml(i, url)))


if __name__ == "__main__":
    
    path = './json/primary/full.json'
    audio_ =set()
    with open(path, 'r') as f:
        f_ = json.load(f)
        for i, item in enumerate(f_):
            url = item['url']
            audio_.add(url)
    for i, url in enumerate(audio_):
        bilibili().run(i, url)
        time.sleep(3)