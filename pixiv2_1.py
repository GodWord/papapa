import re
import requests
import os
from datetime import timedelta
from datetime import date as da
import json


class Pixiv:

    def __init__(self):
        self.R = requests.session()
        self.pixiv_id = None
        self.password = None
        self.date_mode = self.date = str(da.today() - timedelta(days=1)).replace('-', '')
        self.root = os.getcwd()

    def login(self, id_, password):
        """
        登录
        :param id_: 帐号
        :param password:密码
        """
        url_for_key = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        login_headers = {'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
        if not self.pixiv_id:
            self.pixiv_id = id_
            self.password = password
        else:
            self.R.cookies.clear()
        r = self.R.get(url=url_for_key, headers=login_headers)
        post_key = re.search(r'\.postKey":"(.+?)"', r.text).group(1)

        login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        data = {'pixiv_id': self.pixiv_id,
                'password': self.password,
                'post_key': post_key,
                'return_to': 'https://www.pixiv.net/'
                }
        self.R.post(url=login_url, headers=login_headers, data=data)

    def get_rank_r18(self, pages=1, work_type='', mode='daily', date=None):
        """
        获取限制级排行榜的信息
        :param pages: 页数，一页对应50个作品，限制级作品最大支持2页
        :param work_type:作品类型，有综合、插画、漫画，对应输入空字符串、illust、manga，默认综合
        :param mode:排行模式，有daily、weekly、male、female，对应日排、周排、受男性欢迎、受女性欢迎，默认日排
        :param date:输入排行日期，为8数字字符串yyyymmdd
        :return:返回排行榜信息details供downloader下载
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
        urls = []
        if date:
            self.date = date
        if work_type in ['', 'illust', 'manga']:
            content = '&content=' + work_type
            if work_type == '':
                content = ''
                self.w_type = '(综合排行)'
            else:
                self.w_type = '({}排行)'.format(work_type)
        else:
            raise ValueError('无此作品类型')

        if mode in ['daily', 'weekly', 'male', 'female']:
            if mode == 'daily':
                self.date_mode = self.date + '_r18'
            elif mode == 'weekly':
                self.date_mode = '截至' + self.date + '周排_r18'
            elif mode == 'male':
                self.date_mode = self.date + '受男性欢迎_r18'
            else:
                self.date_mode = self.date + '受女性欢迎_r18'
        else:
            raise ValueError('无此排行类型')
        for i in range(1, pages + 1):
            urls.append('https://www.pixiv.net/ranking.php?mode={}_r18&date={}&p={}&format=json{}'.format(mode, self.date, i, content))
            self.date = str(da.today() - timedelta(days=1)).replace('-', '')
        return self.extract_details(urls, headers)

    def get_rank(self, pages=1, work_type='', mode='daily', date=None):
        """
        获取正常排行榜的信息
        :param pages: 页数，一页对应50个作品，正常作品最大支持10页
        :param work_type: 作品类型，有综合、插画、漫画，对应输入空字符串、illust、manga，默认综合
        :param mode: 排行模式，输入daily、weekly、monthly、rookie、original、male、female、，对应日排、周排、月排、新人、原创、受男性欢迎、受女性欢迎，其中后三种是综合独有的
        :param date:输入排行日期，为8数字字符串yyyymmdd
        :return:返回排行榜信息details供downloader下载
        """
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
        urls = []
        if date:
            self.date = date

        if work_type in ['', 'illust', 'manga']:
            content = '&content=' + work_type
            if work_type == '':
                content = ''
                self.w_type = '(综合排行)'
            else:
                self.w_type = '({}排行)'.format(work_type)
        else:
            raise ValueError('无此作品类型')

        if mode in ['daily', 'weekly', 'monthly', 'rookie', 'original', 'male', 'female']:
            if mode == 'daily':
                self.date_mode = self.date
            elif mode == 'weekly':
                self.date_mode = '截至' + self.date + '周排'
            elif mode == 'monthly':
                self.date_mode = '截至' + self.date + '月排'
            elif mode == 'rookie':
                self.date_mode = self.date + '新人'
            elif work_type == 'daily' and mode == 'original':
                self.date_mode = self.date + '原创'
            elif work_type == 'daily' and mode == 'male':
                self.date_mode = self.date + '受男性欢迎'
            elif work_type == 'daily' and mode == 'female':
                self.date_mode = self.date + '受女性欢迎'
            else:
                raise ValueError('作品类型与排行类型不匹配')
        else:
             raise ValueError('无此排行类型')
        for i in range(1, pages + 1):
            urls.append('https://www.pixiv.net/ranking.php?mode={}&date={}&p={}&format=json{}'.format(mode, self.date, i, content))
        self.date = str(da.today() - timedelta(days=1)).replace('-', '')
        return self.extract_details(urls, headers)

    def extract_details(self, urls, headers):
        self.ids = []; self.titles = []; self.user_names = []; self.illust_type = []; self.illust_page_count = []; self.ts = []
        for url in urls:
            r = self.R.get(url, headers=headers)
            data = json.dumps(r.json(), ensure_ascii=False)
            self.ids.extend(re.findall(r'illust_id": (\d+),', data))  # 作品id,登记查重
            self.titles.extend(re.findall(r'"title": "(.+?)"', data))  # 作品名
            self.user_names.extend(re.findall(r'name": "(.+?)"', data))  # 作者名
            self.illust_type.extend(re.findall(r'illust_type": "(\d)"', data))  # 类型0 work，类型1 manga
            self.illust_page_count.extend(re.findall(r'page_count": "(\d+)"', data))  # 图片数量
            self.ts.extend(re.findall(r'master(/img(?:/\d+)+)', data))
        print(len(self.ids), self.ids)
        print(len(self.titles), self.titles)
        print(len(self.user_names), self.user_names)
        print(len(self.illust_type), self.illust_type)
        print(len(self.illust_page_count), self.illust_page_count)
        print(len(self.ts), self.ts)
        return self.ids, self.titles, self.user_names, self.illust_type, self.illust_page_count, self.ts

    def downloader(self, details):
        """
        接收排行榜信息，自动完成排行榜作品的下载
        :param details: 排行榜信息
        """
        path = self.root + '/Pixiv/' + self.date_mode + self.w_type
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)
        for i in range(len(details[0])):
            if details[3][i] == '0' and details[4][i] == '1':
                self.single_d(details[0][i], details[1][i], details[2][i], details[5][i])
            elif details[3][i] == '0' and details[4][i] != '1':
                self.multiple_d(details[0][i], details[1][i], details[2][i], details[5][i], details[4][i])
            elif details[3][i] == '1':
                self.multiple_d(details[0][i], details[1][i], details[2][i], details[5][i], details[4][i], manga=True)
            else:
                continue
        print('心から作家たちに感謝してる')

    def multiple_d(self, id_, title, user_name, t, pages, manga=False):
        urls = []
        com = re.compile(r'\\u3000|[\\/:*?"<>|]+?')
        user_name = re.sub(com, '_', user_name)
        title = re.sub(com, '_', title)
        if manga:
            manga = 'manga'
        else:
            manga = ''
        direction = './{} [{}] {} ({})'.format(manga, user_name, title, id_)  # 多线程请修改为绝对路径
        os.makedirs(direction)
        os.chdir(direction)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}

        if pages == '1':
            headers['Referer'] = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + id_
            urls.append('https://i.pximg.net/img-original{}_p0.jpg'.format(t))  # 下载出错是换图片后缀
        else:
            headers['Referer'] = 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=' + id_
            urls = ['https://i.pximg.net/img-master{}_p{}_master1200.jpg'.format(t, i) for i in range(int(pages))]
        for j in range(int(pages)):
            img_r = self.R.get(urls[j], headers=headers)
            with open(str(j) + '.jpg', 'wb') as img:
                if img_r.status_code != 404:
                    img.write(img_r.content)
                else:
                    img.write(self.R.get(urls[j].replace('jpg', 'png'), headers=headers).content)
        os.chdir('..')

    def single_d(self, id_, title, user_name, t):
        com = re.compile(r'\\u3000|[\\/:*?"<>|]+')
        user_name = re.sub(com, '_', user_name)
        title = re.sub(com, '_', title)
        img_name = '[{}] {} ({}).jpg'.format(user_name, title, id_)
        url = 'https://i.pximg.net/img-original{}_p0.jpg'.format(t)
        headers = {'Referer': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + id_,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
        img_r = self.R.get(url, headers=headers)
        with open(img_name, 'wb') as img:
            if img_r.status_code != 404:
                img.write(img_r.content)
            else:
                img.write(self.R.get(url.replace('jpg', 'png'), headers=headers).content)

    def get_author_works(self, author_id=789222, page=1, work_type='all'):
        """
        获取某个作家的作品
        :param author_id: 作家的id
        :param page: 获取多少页作品，一页20个作品
        :param work_type: 作品筛选，输入all、illust、manga，对应无筛选，筛选插画，筛选漫画
        """
        author_id = str(author_id)
        j = 0
        ids = []; titles = []; illust_type = []; illust_pages=[]; ts=[]
        headers = {'Referer': 'https://www.pixiv.net/member_illust.php?id={}&type=all'.format(author_id),
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
        if work_type not in ['all', 'illust', 'manga']:
            raise ValueError('无此作品类型')
        for i in range(1, page + 1):
            url = 'https://www.pixiv.net/member_illust.php?id={}&type={}&p={}'.format(author_id, work_type, str(i))
            data = self.R.get(url, headers=headers).text
            if re.findall(r'illust_id=(\d+?)"><h1', data):
                ids.extend(re.findall(r'illust_id=(\d+?)"><h1', data))
                titles.extend(re.findall(r'"title" title="(.+?)"', data))
                user_name = re.search(r'<title>「(.+)」', data).group(1)
                illust_type.extend(re.findall(r'\d"class="(.+?)"><div class="_layout', data))
                ts.extend(re.findall(r'master(/img(?:/\d+)+)', data))
                if re.findall(r'span>(\d+)</span', data):
                    illust_pages.extend(re.findall(r'span>(\d+)</span', data))
            else:
                break
        print(len(ids), ids)
        print(len(titles), titles)
        print(len(illust_type), illust_type)
        print(len(illust_pages), illust_pages)
        print(len(ts), ts)

        path = self.root + '/Pixiv/{}({})'.format(user_name, author_id)
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)
        for i in range(len(ids)):
            if illust_type[i] == 'work  _work   ':
                self.single_d(ids[i], titles[i], user_name, ts[i])
            elif illust_type[i] == 'work  _work multiple   ':
                self.multiple_d(ids[i], titles[i], user_name, ts[i], illust_pages[j])
                j += 1
            elif illust_type[i] == 'work  _work manga multiple   ':
                self.multiple_d(ids[i], titles[i], user_name, ts[i], illust_pages[j], manga=True)
                j += 1
            elif illust_type[i] == 'work  _work manga   ':
                self.single_d(ids[i], titles[i], user_name, ts[i])
            else:
                continue

    def vip(self):
        # 热门筛选开发中
        pass

    def tag_select(self):
        #标签筛选开发中
        pass


p = Pixiv()
p.login('1111111111', '2222222')
details = p.get_rank()
p.downloader(details)

#单页插画
#https://i.pximg.net/img-original/img/2018/07/19/00/09/57/69754095_p0.png

#manga
#https://i.pximg.net/img-master/img/2018/07/20/19/10/56/69776197_p1_master1200.jpg

#multiple illust
#https://i.pximg.net/img-master/img/2018/07/19/17/49/40/69761818_p0_master1200.jpg
