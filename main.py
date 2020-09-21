import requests
import string
import random
import time
import re
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup


class ConnectionManager:

    def __init__(self):
        self.new_ip = "0.0.0.0"
        self.old_ip = "0.0.0.0"
        self.new_identity()

    @classmethod
    def _get_connection(cls):
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="imgbbcom")
            controller.signal(Signal.NEWNYM)
            controller.close()

    @classmethod
    def request(cls, url):
        proxies = {
            'http': 'socks5://localhost:9050',
            'https': 'socks5://localhost:9050'
        }
        headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/535.1 (KHTML, '
                                 'like Gecko) Chrome/13.0.782.20 Safari/535.1'}
        out = requests.get(url, proxies=proxies, headers=headers)
        return out

    def new_identity(self):
        if self.new_ip == "0.0.0.0":
            self._get_connection()
            self.new_ip = self.request("http://icanhazip.com/").text
        else:
            self.old_ip = self.new_ip
            self._get_connection()
            self.new_ip = self.request("http://icanhazip.com/").text

        seg = 0
        while self.old_ip == self.new_ip:
            time.sleep(5)
            seg += 5
            print("Ожидаем получения нового IP: %s секунд" % seg)
            self.new_ip = self.request("http://icanhazip.com/").text
        print("Новое подключение с IP: %s" % self.new_ip, end='')


def random_link():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


def save_image(url, filename):
    r = requests.get(url)
    with open(filename, 'wb') as imgfile:
        imgfile.write(r.content)


counter = 0
cm = ConnectionManager()
while True:
    main_link = 'https://ibb.co/' + random_link()
    req = cm.request(main_link)

    status_code = req.status_code if req != '' else -1
    if status_code == 200:
        html = BeautifulSoup(req.text, "html.parser")
        title = html.title.string[0:-8].replace(' ', '-')
        print(title)
        for link in html.find_all('a', attrs={'download': re.compile("^{}".format(title))}):
            download_link = link.get('href')
            print(download_link)
            save_image(download_link, title + '.jpg')
        print(req.status_code, " - ", main_link)
    else:
        print(req.status_code, " - ", main_link)

    counter += 1
    if counter % 5 == 0:
        cm.new_identity()
