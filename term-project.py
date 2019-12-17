import time
import random
from bs4 import BeautifulSoup
import pandas as pd
from itertools import count
from selenium import webdriver
import webbrowser
from konlpy.tag import Hannanum
from collections import Counter
from itertools import chain
import pickle
import pytagcloud

category_num = [3301, 3302, 3303, 3305, 3307, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316
               , 3317, 3319, 3321, 3323, 3325, 3328, 3329]

category_dic = {3301:'컴퓨터공학', 3302:'IT일반', 3303:'컴퓨터입문_활용', 3305:'전산통계_해석', 3307:'OS', 3309:'네트워크'
                , 3310:'보안_해킹', 3311:'데이터베이스', 3312:'개발방법론', 3313:'게임', 3314:'웹프로그래밍', 3315:'프로그래밍언어'
                , 3316:'모바일프로그래밍', 3317:'OA_사무자동화', 3319:'웹사이트', 3321:'그래픽', 3323:'멀티미디어', 3325:'CAD'
                , 3328:'자격증_수험서' , 3329:'대학교재'}

r = lambda: random.randint(0, 255)
color = lambda: (r(), r(), r())

def get_kobomungo_data():
    result = []
    wd = webdriver.Chrome('C:/Users/chunso/AppData/Local/Programs/Python/Python37/webDriver/chromedriver.exe')
    for category_idx in category_num:
        kobomungo_URL = "http://www.kyobobook.co.kr/categoryRenewal/categoryMain.laf?linkClass=%s&mallGb=KOR&orderClick=sgx" %str(category_idx)
        wd.get(kobomungo_URL)
        print ("Category Index [%s] Called" % (str(category_idx)))
        time.sleep(5)
        tmp = []
        
        for page_idx in count():
            try:
                wd.execute_script("_go_targetPage('%s')" % str(page_idx + 1))
                print ("PageIndex [%s] Called" % (str(page_idx + 1)))
            except Exception as e:
                break
            
            time.sleep(3)
            rcv_data = wd.page_source  
            soupData = BeautifulSoup(rcv_data, 'html.parser')
            book_list = soupData.findAll('li', attrs={'class': 'id_detailli'})
            
            for book in book_list:
                book_rank = book.find('em', attrs={'class': 'best_flag'}).find('span').string
                book_title = remove_bracket(book.find('div', attrs={'class': 'title'}).find('strong').string)
                book_author = remove_bracket(book.find('div', attrs={'class': 'pub_info'}).find('span', attrs={'class': 'author'}).string)
                book_publication = remove_bracket(book.find('div', attrs={'class': 'pub_info'}).find('span', attrs={'class': 'publication'}).string)
                book_sumary = remove_bracket(book.find('div', attrs={'class': 'info'}).find('span').string)
                
                print(book_rank , book_title)
                tmp.append([book_rank] + [book_title] + [book_author] + [book_publication] + [book_sumary])
        result.append([category_idx] + [tmp])
    return result

def remove_bracket(s):
    if(str(type(s)) != "<class 'str'>"):
        s = str(s)
    return s.replace("("," ").replace(")", " ")

def abstract_title(book_list):
    title_list = []
    for category in book_list:
        for book in category[1]:
            title_list.append(book[1])
    return title_list

def text_mining(title_list, ntags=50, multiplier=1):
    h = Hannanum()
    data_nouns = []
    for title in title_list:
        data_nouns.extend(h.nouns(title))
    
    count = Counter(data_nouns)
    
    return [{'color': color(),'tag':n,'size':int(c*multiplier*0.5)} for n,c in count.most_common(ntags)]

def draw_wordcloud(tags, filename, fontname = 'Noto Sans CJK',size1 = (1300,800)):
    pytagcloud.create_tag_image(tags, filename, fontname=fontname, size=size1)
    webbrowser.open(filename)
    return

def save_data(book_list):
    for category in book_list:
        category_name = category_dic[category[0]]
        book_table = pd.DataFrame(category[1], columns=('순위', '제목', '저자', '출판사', '요약'))
        book_table.to_csv("./%s분야_베스트셀러_list.csv" %str(category_name), encoding="cp949", mode='w', index=False)
    return

def main():
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('!!!!!!!!!!!!!!!!!!!!!PARKCHUNSO TERM PROJECT START!!!!!!!!!!!!!!!!!!!!!')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    print('')
    print('CRAWLING START')
    book_list = get_kobomungo_data()
    print('CRAWLING FINISH')
    print('')

    print('')
    print('TEXTMINING START')
    title_list = abstract_title(book_list)
    draw_data = text_mining(title_list)
    print('TEXTMINING FINISH')
    print('')

    print('')
    print('RESULT SAVE START')
    draw_wordcloud(draw_data, "WordCloud.png")
    save_data(book_list)
    print('RESULT SAVE FINISH')
    print('')
    
    print('FINISHED')
    
if __name__ == '__main__':
     main ()
