#coding='utf-8'
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
import time as t
import re
from bs4 import BeautifulSoup
import xlrd
import xlwt
import os

#先进入浏览器知网
driver = webdriver.Firefox()
driver.minimize_window()#浏览器窗口最小化，只显示dos窗口
driver.get('https://www.cnki.net/')
def cut(list,n):
        """将列表按特定数量切分成小列表"""
        for i in range(0,len(list),n):
            yield list[i:i+n] 
def clear(old_list,new_list):
        """用于清洗出纯文本"""
        for i in old_list:
            n=(i.text).strip()
            n=n.replace('\n',' ')
            new_list.append(n)
        return new_list 
def clear_jou(old_list,new_list):
        """用于清洗出期刊的纯文本"""
        for i in old_list:
            n=(i.text).strip()
            n=n.replace('\n',' ')
            new_list.append(n)
        return new_list 
def clear_ab(old_list,new_list):
        """用于清洗出摘要的纯文本"""
        for i in old_list:
            n=(i.text).strip()
            n=n.replace('\n','')
            n=n.replace('摘要：','')
            n=n.replace(' ','')
            new_list.append(n)
        return new_list
def clear_c(old_list,new_list):
        """用于清洗出被引数的纯文本"""
        for i in old_list:
            n=str(i)
            n=n.replace('\n','')
            new_list.append(i)
        return new_list 
def clear_d(old_list,new_list):
        """用于清洗出下载量的纯文本"""
        for i in old_list:
            n=(i.text).strip()
            n=n.replace('\n',' ')
            n=int(n)
            new_list.append(n)
        return new_list 
def extract(inpath):
    """取出基金号"""
    data = xlrd.open_workbook(inpath, encoding_override='utf-8')
    table = data.sheets()[0]#选定表
    nrows = table.nrows#获取行号
    ncols = table.ncols#获取列号
    numbers=[]
    for i in range(1, nrows):#第0行为表头
        alldata = table.row_values(i)#循环输出excel表中每一行，即所有数据
        result = alldata[4]#取出表中第一列数据
        numbers.append(result)
    return numbers
def save_afile(alls,keywords,file):
    os.chdir(r'F:\图情社科基金项目数据爬取\论文信息')#进入要保存的文件夹
    """将一个基金的论文数据保存在一个excel"""
    f=xlwt.Workbook()
    sheet1=f.add_sheet(u'sheet1',cell_overwrite_ok=True)
    sheet1.write(0,0,'题目')
    sheet1.write(0,1,'发表期刊')
    sheet1.write(0,2,'出版时间')
    sheet1.write(0,3,'摘要')
    i=1
    for all in alls:#遍历每一页
        for data in all:#遍历每一行
            for j in range(len(data)):#取每一单元格
                sheet1.write(i,j,data[j])#写入单元格
            i=i+1#往下一行
    f.save(file+'.xls')
    #保存关键词为txt
    file = open(file+'.txt', 'w')  
    for key in keywords:  
        file.write(str(key))  
        file.write('\n') 
    file.close()  
def get_html(number,count_number):
        """火狐模拟并获得当前源码
             第一个是网址self.url,第二个是基金号，需要导入基金号列表
        """
        """火狐模拟并获得当前源码
             第一个是基金号,第二个是计数器
        """
        s_2='/html/body/div[4]/div/div[2]/div[1]/input[1]'
        s_1='//*[@id="txt_SearchText"]'
        if  count_number==0:
            element=driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[1]/div/div[1]/span')#鼠标悬浮
            ActionChains(driver).move_to_element(element).perform()
            t.sleep(2)
            driver.find_element_by_link_text(u'基金').click()#选中为基金检索模式
            driver.find_element_by_xpath(s_1).send_keys(str(number))#键入基金号
            driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[1]/input[2]').click()#进行搜索
        else:
            driver.find_element_by_xpath(s_2).clear()#清除内容
            driver.find_element_by_xpath(s_2).send_keys(str(number))#键入基金号
            driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[1]/input[2]').click()#进行搜索
        t.sleep(2)
        try:
            driver.find_element_by_css_selector('#DivDisplayMode > li:nth-child(1)').click()#选中为详情,如果有问题，需要设置为断点
            t.sleep(5)
            html_now= driver.page_source#页面源码
            print('ok!') 
        except:
            html_now='下一个'
        finally:
            return html_now
def pull(html):
        """提取一页的论文条目、关键词和当前页面数"""
        soup = BeautifulSoup(html,'html.parser')    #解析器：html.parser
        try:
            page=soup.select('.countPageMark')#页面计数
            count=page[0].text
        except:
            count=1

        title=soup.select('.middle>h6>a')
        titles=[]#纯标题
        clear(title,titles)
     
        journal=soup.select('.middle p.baseinfo span a ')#期刊名
        date=soup.select('.middle p.baseinfo span.date')#发表时间

        journals_o=[]#取出字符
        journals=[]#最终结果
        clear_jou(journal,journals_o)
        for i in journals_o:
            if i.isdigit():#如果该项为数字
                pass
            else:
                journals.append(i)
        
        dates=[]
        clear(date,dates)

        abstract=soup.select('.abstract')#摘要
        abstracts=[]
        clear_ab(abstract,abstracts)
        keyword=soup.select('.keywords>a')#关键词
        keywords=[]
        clear(keyword,keywords)
        page=[]#除了关键词的所有信息
        for i in range(len(titles)):
            page.append(titles[i:i+1]+journals[i:i+1]+dates[i:i+1]+abstracts[i:i+1])
        return page,keywords,count

def one_n_save(fund,count_number):
    """保存一个基金号的相关数据"""
    alls=[]#一个基金的所有页面
    keywords=[]#一个基金的所有关键词
    all,key_words,count=pull(get_html(str(fund),count_number))#第一页的数据
    count=str(count)
    count=count.replace('1/','')
    alls.append(all)#存储第一页的数据
    keywords.append(key_words)#存储第一页的关键词
    t.sleep(5)
    #一个基金的大部分数据，关键词，页数
    while True:
        if 1<int(count)<3:#只有两页
            t.sleep(5)
            try:
                driver.find_element_by_xpath('//*[@id="Page_next_top"]').click()#点击翻到第二页
            except:
                driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[3]').click()#点击翻到第二页
            t.sleep(5)
            html_a= driver.page_source#当前页面源码
            all,key_words,count_1=pull(html_a)
            alls.append(all)#存储当页的数据
            keywords.append(key_words)
            break
        elif int(count)>=3:#大于两页
            t.sleep(5)
            try:
                driver.find_element_by_xpath('//*[@id="Page_next_top"]').click()#点击翻到第二页
            except:
                driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[3]').click()#点击翻到第二页
            t.sleep(5)
            html_a= driver.page_source#当前页面源码
            all,key_words,count_2=pull(html_a)
            alls.append(all)#存储当页的数据
            keywords.append(key_words)
            for i in range(int(count)-2):#翻几次页
                t.sleep(5)
                try:
                    driver.find_element_by_xpath('//*[@id="Page_next_top"]').click()#点击翻到第二页
                except:
                    driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[4]').click()#点击翻页
                t.sleep(5)
                html_a= driver.page_source#当前页面源码
                all,key_words,count_go=pull(html_a)
                alls.append(all)#存储当页的数据
                keywords.append(key_words)
            break
        else:
            break
    save_afile(alls,keywords,str(fund))
    print("成功！")


#inpath = '列表.xlsx'#excel文件所在路径
#ns=extract(inpath)#基金号列表
count_number=0
#只能存储有论文的
#
i='14BTQ073'#单个基金号的论文元数据爬取，多个遍历即可
#for i in ns:
one_n_save(i,count_number)#保存这一基金号的
print(str(i)+'基金号的所有论文基本信息保存完毕！')#显示成功信息
#count_number=count_number+1
driver.quit()#关闭浏览器
print('Over！')#全部完成

#本程序仅能自动获取有论文的情况
#出现了被引数错误的情况——clear_c有问题
#出现了下载数出现在被引数的情况——获取被引数和下载量有问题
#出现了事实上下载量和被引数都没有但写入到excel的情况，定位同上
#决定放弃被引数和下载量的爬取
#将被引数和下载量放在另一个程序中










