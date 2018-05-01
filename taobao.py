import openpyxl #第三方excel操作
from datetime import date
import re
import json
import requests
def taobao(keyword,pages,select_type,date_):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'}
    url = 'https://s.taobao.com/search?q={}&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id={}&ie=utf8&sort={}'.format(keyword, date_, selections[select_type])
    titles=[];item_ids=[];prices=[];locations=[];sales=[];seller_ids=[];store_names=[]
    for i in range(pages):
        r = requests.get(url+'&s={}'.format(str(i*44)),headers=headers,)

        data = re.search(r'g_page_config = (.+);',r.text)#捕捉json字符串
        data = json.loads(data.group(1),encoding='utf-8')#json转dict
        for auction in data['mods']['itemlist']['data']['auctions']:
            titles.append(auction['raw_title'])#商品名
            item_ids.append(auction['nid'])#商品id
            prices.append(auction['view_price'])#价格
            locations.append(auction['item_loc'])#货源
            sales.append(auction['view_sales'])#卖出数量
            seller_ids.append(auction['user_id']) #商家id
            store_names.append(auction['nick'])#店铺名

        #正则实现
        '''titles.extend(re.findall(r'"raw_title":"(.+?)"',r.text,re.I)) 
        item_ids.extend( re.findall(r'"nid":"(.+?)"',r.text,re.I))
        prices.extend(re.findall(r'"view_price":"([^"]+)"',r.text,re.I)) 
        locations.extend(re.findall(r'"item_loc":"([^"]+)"',r.text,re.I))
        sales.extend(re.findall(r'"view_sales":"([^"]+)"',r.text,re.I)) 
        seller_ids.extend(re.findall(r'"user_id":"([^"]+)"',r.text,re.I)) 
        store_names.extend(re.findall(r'"nick":"([^"]+)"',r.text,re.I)) '''
    #单纯打印出来看
    print (len(titles),len(item_ids),len(prices),len(locations),len(sales),len(seller_ids),len(store_names))
    print(titles)
    print(item_ids)
    print(prices)
    print(locations)
    print(sales)
    print(seller_ids)
    print(store_names)

    #写入excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = keyword
    ws.column_dimensions['A'].width = 70
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['F'].width = 14
    ws.column_dimensions['G'].width = 25
    ws.append([None,'商品id','价格','货源','卖出量','商家id','店铺名'])
    for a in range(len(titles)):
        ws.append([titles[a],item_ids[a],int(re.search(r'(\d+)\.',prices[a]).group(1)),locations[a],int(re.search(r'(\d+)',sales[a]).group(1)),seller_ids[a],store_names[a]])
    wb.save(keyword+'.xlsx')








selections = {'0':'default',
              '1':'renqi-desc',
              '2':'sale-desc'}
keyword = input('输入商品名\n')
pages = int(input('爬多少页\n'))
date_ =  'staobaoz_' + str(date.today()).replace('-','')
if input('yes/no  for 改排序方式,默认综合')=='yes':
    select_type = input('输入1按人气，输入2按销量')
else:
    select_type = '0'
taobao(keyword,pages,select_type,date_)
