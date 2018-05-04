import requests
import re
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
                   }
def get_ids(keyword,psort):
    ids = []
    pages = int(input("爬商品前几页,每页30个商品"))
    for i in range(1,pages+1):
        url = 'https://search.jd.com/Search?keyword={}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&psort={}&click=0&page={}&s={}'.format(keyword,psort,str(i*2-1),str(60*i-59))
        r = requests.get(url,headers=headers)
        response = r.content.decode('utf-8')
        ids.extend(re.findall(r'li data-sku="(\d+)"',response))
    print(len(ids),ids)
    if input('是否只爬前几件商品yes/no')=='yes':
        nums = int(input('只爬前n件商品,n<={}'.format(len(ids))))
    else:
        nums = len(ids)
    return ids,nums

def get_comment(ids_and_nums):
    pages = int(input('爬评论的前几页,10个评论每页'))
    for num in range(ids_and_nums[1]):
        comments = [];types = [];scores = []
        f.write('https://item.jd.com/{}.html '.format(ids_and_nums[0][num])+'\n\n')
        for i in range(pages):
            url = 'https://club.jd.com/productpage/p-{}-s-0-t-1-p-{}.html'.format(ids_and_nums[0][num],str(i))
            r = requests.get(url,headers=headers)
            for each in r.json()['comments']:
                f.write('得分：{}\n'.format('*' *int(each['score'])))
                f.write('评论：'+each['content']+'\n')
                f.write('类型：'+each['productColor']+'\n\n')
                #列表储存，需要时使用
                #comments.append(each['content'])
                #types.append(each['productColor'])
                #scores.append(each['score'])
        f.write('\n\n\n\n')


keyword = input("请输入商品名")
psort = input("请输入排序的数字代号，0：默认综合 3：按销量 4：按评论")
ids_and_nums=get_ids(keyword,psort)
with open(keyword+'.txt','w',encoding='utf-8') as f:
    get_comment(ids_and_nums)

#通用json，但是只按时间排序
#https://club.jd.com/productpage/p-1982079424-s-0-t-1-p-0.html
#通用json但是只按推荐排序
#https://sclub.jd.com/comment/productPageComments.action?productId=3281156&score=0&sortType=5&page=1&pageSize=10&isShadowSku=0&rid=0&fold=1
