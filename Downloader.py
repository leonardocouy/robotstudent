from urllib import request
import http.cookiejar as cookielib

url_login = 'http://www.unipacbomdespacho.com.br/v2/'


class Downloader():
    def __init__(self, cookies, url, folder):
        self.downloader = request.build_opener()
        self.load_cookies(cookies)
        self.url = url
        self.folder = folder + '/'

    def load_cookies(self, cookies):
        cj = cookielib.LWPCookieJar()
        for cookie in cookies:
            cj.set_cookie(cookielib.Cookie(
                version=0, name=cookie['name'], value=cookie['value'],
                domain=cookie['domain'], domain_specified=True, domain_initial_dot=False,
                path=cookie['path'], path_specified=True, secure=cookie['secure'],
                expires=None, comment=None, comment_url=None, rest=None, discard=False,
                port=None, port_specified=False, rfc2109=False
            ))
        self.downloader.add_handler(request.HTTPCookieProcessor(cj))

    def download(self):
        request.install_opener(self.downloader)
        content = self.downloader.open(self.url)
        filename = content.geturl().split('/')[-1].replace('%20', '-')
        if not filename.endswith('.exe'):
            with open(self.folder + filename, 'wb') as f:
                f.write(content.read())

    def run(self):
        self.download()