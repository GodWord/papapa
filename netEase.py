import json
import re
from Crypto.Cipher import AES#新的加密模块只接受bytes数据，否者报错，密匙明文什么的要先转码
import base64
import binascii
import random
import requests
from math import ceil

secret_key = b'0CoJUm6Qyw8W8jud'#第四参数，aes密匙
pub_key ="010001"#第二参数，rsa公匙组成
modulus = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"#第三参数，rsa公匙组成
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'}

#生成随机长度为16的字符串的二进制编码
def random_16():
    return bytes(''.join(random.sample('1234567890DeepDarkFantasy',16)),'utf-8')

#aes加密
def aes_encrypt(text,key):
    pad = 16 - len(text)%16#对长度不是16倍数的字符串进行补全，然后在转为bytes数据
    try:					#如果接到bytes数据（如第一次aes加密得到的密文）要解码再进行补全
        text = text.decode()
    except:
        pass
    text = text + pad * chr(pad)
    try:
        text = text.encode()
    except:
        pass
    encryptor = AES.new(key,AES.MODE_CBC,b'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)#得到的密文还要进行base64编码
    return ciphertext

#rsa加密
def rsa_encrypt(ran_16,pub_key,modulus):
    text = ran_16[::-1]#明文处理，反序并hex编码
    rsa = int(binascii.hexlify(text), 16) ** int(pub_key, 16) % int(modulus, 16)
    return format(rsa, 'x').zfill(256)

#返回加密后内容
def encrypt_data(data):
    ran_16 = random_16()
    text = json.dumps(data)
    params = aes_encrypt(text,secret_key)
    params = aes_encrypt(params,ran_16)
    encSecKey = rsa_encrypt(ran_16,pub_key,modulus)
    return  {'params':params.decode(),
             'encSecKey':encSecKey  }


#以上是加密算法

#获取歌单id
def get_playlists(pages,order,cat):
    playlist_ids = []
    for page in range(pages):
        url = 'http://music.163.com/discover/playlist/?order={}&cat={}&limit=35&offset={}'.format(order,cat,str(page*35))
        r = requests.get(url,headers=headers)
        playlist_ids.extend(re.findall(r'playlist\?id=(\d+?)" class="msk"',r.text))
        return playlist_ids
		
#获取歌曲id
def get_songs(playlist_id='778462085'):
    r = requests.get('http://music.163.com/playlist?id={}'.format(playlist_id),headers=headers)
    song_ids = re.findall(r'song\?id=(\d+?)".+?</a>',r.text)
    song_titles = re.findall(r'song\?id=\d+?">(.+?)</a>',r.text)
    list_title = re.search(r'>(.+?) - 歌单 - 网易云音乐',r.text).group(1)
    list_url = 'http://music.163.com/playlist?id='+playlist_id
    return [song_ids, song_titles, list_title, list_url]




#以非常简陋的txt保存评论
def save_comments(some,pages,f):
    f.write('\n\n\n歌单《{}》\t\t链接{}'.format(some[2], some[3]).center(200) + '\n\n\n')
    post_urls = ['http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + deep + '?csrf_token=' for deep in some[0]]
    song_urls = ['http://music.163.com/song?id=' + dark for dark in some[0]]

    for i in range(len(post_urls)):
        f.write('歌曲「{}」\t\t链接{}\n\n'.format(some[1][i],song_urls[i]))
        for j in range(pages):
            if j == 0: #第一页会包括精彩评论和最新评论
                data = {'rid':"", 'offset':'0', 'total':"true", 'limit':"20", 'csrf_token':""}
                enc_data = encrypt_data(data)
                r = requests.post(post_urls[i], headers=headers, data=enc_data)
                content = r.json()
                if content['hotComments']:#判断第一页有没有精彩评论
                    f.write('\n\n********' + '精彩评论\n\n')
                    comment(content, 'hotComments', f)

                f.write('\n\n********'+'最新评论\n\n')
                comment(content,'comments',f)

            else: #非第一页只有普通评论
                data = {'rid':"", 'offset':str(j*20), 'total':"false", 'limit':"20", 'csrf_token':""}
                enc_data = encrypt_data(data)
                r = requests.post(post_urls[i],headers=headers,data=enc_data)
                content = r.json()
                comment(content,'comments',f)


#提取json数据中的评论，因为评论分两种，所以设一个参数接收种类
def comment(content,c_type,f):
    for each in content[c_type]:
        if each['beReplied']:#判断有没有回复内容
            if each['beReplied'][0]['content']:#有时回复内容会被删掉，也判断一下
                f.write('' + each['content'] + '\n')
                f.write('\t回复:\n' + each['beReplied'][0]['content'] + '\n' + '-' * 50 + '\n')
        else:
            f.write('' + each['content'] + '\n' + '-' * 60 + '\n')




#single_crawl接收两个个参数，是歌单id字符串默认'778462085'，爬取页数默认为1
def single_crawl(playlist_id='778462085',pages=1):
    with open('playlist_id{}.txt'.format(playlist_id), 'w', encoding='utf-8') as s:
        save_comments(get_songs(playlist_id),pages,s)


#multiple_crawl接收四个参数，nums是必需整形参数，是爬多前少个歌单；order，cat是可选参数，分别是排序和分类，排序有new和hot，分类动手找。默认排序hot，默认分类ACG		
def multiple_crawl(nums,order='hot',cat='ACG',pages=1):
    with open('{}_{}_{}lists.txt'.format(order, cat, nums), 'w', encoding='utf-8') as m:
        playlist_ids = get_playlists(ceil(nums/35),order,cat)
        print(playlist_ids)
        for i in range(nums):
            save_comments(get_songs(playlist_ids[i]),pages,m)
#长时间爬取会被服务器踢出，适当时候可以休眠一段时间，或ip代理

multiple_crawl(2)




