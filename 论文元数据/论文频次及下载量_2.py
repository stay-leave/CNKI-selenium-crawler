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
from xlutils.copy import copy
import os


#先进入浏览器知网
driver = webdriver.Firefox()
driver.minimize_window()
driver.get('https://www.cnki.net/')

def clear_c(old_list,new_list):#清洗出被引量
    for i in range(len(old_list)):
        pattern=re.compile('.*?target="_blank">(\d+)</a>]]')
        if pattern.findall(str(old_list[i:i+1]))!=[]:
            ci=pattern.findall(str(old_list[i:i+1]))#list
            ci = "".join(ci)
            ci=int(ci)
        else:
            ci=0
        new_list.append(ci)
def clear_d(old_list,new_list):#清洗出下载量
    for i in range(len(old_list)):
        di=old_list[i:i+1]
        pattern=re.compile('\d+')
        di=pattern.findall(str(di))#肯定至少找到一个0
        if len(di)<2:
            di=0
        else:
            di=di[1]
        new_list.append(di)
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
def save_afile(alls,file):
    os.chdir(r'F:\图情社科基金项目数据爬取\论文信息')
    """将一个基金的论文数据保存在一个excel"""
    rb=xlrd.open_workbook(file+'.xls')
    wb=copy(rb)#在已有的excel里插入新列
    ws=wb.get_sheet(0)
    ws.write(0,4,'被引频次')
    ws.write(0,5,'下载量')
    i=1
    for all in alls:#遍历每一页
        for data in all:#遍历每一行
            for j in range(4,6):#取每一单元格
                ws.write(i,j,data[j-4])#写入单元格
            i=i+1#往下一行
    wb.save(file+'.xls')
   
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
        html_now= driver.page_source#页面源码
        return html_now
def pull(html):
        """提取一页的被引和下载数"""
        soup = BeautifulSoup(html,'html.parser')    #解析器：html.parser
        try:
            page=soup.select('.countPageMark')#页面计数
            count=page[0].text
        except:
            count=1
        title_1=soup.select('html body.rootw div.wrapper div.content.is-filter-on div.main.fr div#briefBox form div#gridTable.search-result table.result-table-list tbody tr.odd td.name a.fz14')#论文_1名称，用来计数
        title_2=soup.select('html body.rootw div.wrapper div.content.is-filter-on div.main.fr div#briefBox form div#gridTable.search-result table.result-table-list tbody tr td.name a.fz14')
        title=title_1+title_2
        title=set(title)
        list2_t= list(title.intersection(title))
        nm=len(list2_t)
        cited=[]
        download=[]

        j_number=0
        for i in range(1,nm+1):#遍历当前页面的论文条目
            j_number=j_number+1
            if j_number%2!=0:#如果是奇数，是第一个
                    if soup.select('tr.odd:nth-child('+str(i)+') > td:nth-child(7) > span:nth-child(1) > a:nth-child(1)')!=[]:#如果有被引，那就有下载
                        c=soup.select('tr.odd:nth-child('+str(i)+') > td:nth-child(7) > span:nth-child(1) > a:nth-child(1)')
                        d=soup.select('tr.odd:nth-child('+str(i)+') > td:nth-child(8) > a:nth-child(1)')
           
                    elif soup.select('tr.odd:nth-child('+str(i)+') > td:nth-child(8) > a:nth-child(1)')!=[]:#如果没有被引，但有下载
                        c=str(0)
                        d=soup.select('tr.odd:nth-child('+str(i)+') > td:nth-child(8) > a:nth-child(1)')
           
                    else:
                        c=str(0)
                        d=str(0)
            else:#偶数的
                if soup.select('.result-table-list > tbody:nth-child(2) > tr:nth-child('+str(i)+') > td:nth-child(7) > span:nth-child(1) > a:nth-child(1)')!=[]:
                    c=soup.select('.result-table-list > tbody:nth-child(2) > tr:nth-child('+str(i)+') > td:nth-child(7) > span:nth-child(1) > a:nth-child(1)')
                    d=soup.select('.result-table-list > tbody:nth-child(2) > tr:nth-child('+str(i)+') > td:nth-child(8) > a:nth-child(1)')
            
                elif soup.select('.result-table-list > tbody:nth-child(2) > tr:nth-child('+str(i)+') > td:nth-child(8) > a:nth-child(1)')!=[]:
                    c=str(0)
                    d=soup.select('.result-table-list > tbody:nth-child(2) > tr:nth-child('+str(i)+') > td:nth-child(8) > a:nth-child(1)')
            
                else:
                    c=str(0)
                    d=str(0)
           
            cited.append(c)
            download.append(d)

        citeds=[]
        downloads=[]

        clear_c(cited,citeds)
        clear_d(download,downloads)

        page=[]#被引和下载
        for i in range(nm):
            page.append(citeds[i:i+1]+downloads[i:i+1])
        return page,count

def one_n_save(fund,count_number):
    """保存一个基金号的相关数据"""
    alls=[]#一个基金的所有页面
    all,count=pull(get_html(str(fund),count_number))#第一页的数据
    count=str(count)
    count=count.replace('1/','')
    alls.append(all)#存储第一页的数据
    t.sleep(5)
    #一个基金的论文的被引量、下载量，页数
    while True:
        if 1<int(eval(count))<3:#只有两页
            t.sleep(2)                                   
            try:
                driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[3]').click()#点击翻到第二页
            except:
                driver.find_element_by_xpath('//*[@id="Page_next_top"]').click()#点击翻到第二页
            t.sleep(5)
            html_a= driver.page_source#当前页面源码
            all,count_1=pull(html_a)
            alls.append(all)#存储当页的数据
            break
        elif int(eval(count))>=3:#大于两页
            t.sleep(2)
            try:
                driver.find_element_by_xpath('//*[@id="Page_next_top"]').click()#点击翻到第二页
            except:
                driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[3]').click()#点击翻到第二页
            t.sleep(5)
            html_a= driver.page_source#当前页面源码
            all,count_2=pull(html_a)
            alls.append(all)#存储当页的数据
            for i in range(int(count)-2):#翻几次页
                t.sleep(5)                                    
                try:
                    driver.find_element_by_xpath('//*[@id="Page_next_top"]').click()#点击翻到第二页
                except:
                    driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[4]').click()#点击翻页
                t.sleep(5)
                html_a= driver.page_source#当前页面源码
                all,count_go=pull(html_a)
                alls.append(all)#存储当页的数据
            break
        else:
            break
    save_afile(alls,str(fund))
    print("成功！")

#inpath = '列表.xlsx'#excel文件所在路径
#ns=extract(inpath)#基金号列表
count_number=0
#只能存储有论文的
#for i in ns:
i='14BTQ073'
print(str(i)+'基金号的所有论文频次开始爬取！')
one_n_save(i,count_number)#保存这一基金号的
print(str(i)+'基金号的所有论文频次保存完毕！')
driver.quit()
#count_number=count_number+1











