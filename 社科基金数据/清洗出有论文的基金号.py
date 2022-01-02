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


driver = webdriver.Firefox()
driver.minimize_window()
driver.get('https://www.cnki.net/')
def get_html(number,count_number):
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
            #print('ok!') 
        except:
            html_now='下一个'
        finally:
            return html_now
def extract(inpath):
    """取出基金号"""
    data = xlrd.open_workbook(inpath, encoding_override='utf-8')
    table = data.sheets()[0]#选定表
    nrows = table.nrows#获取行号
    ncols = table.ncols#获取列号
    numbers=[]
    for i in range(1, nrows):#第0行为表头
        alldata = table.row_values(i)#循环输出excel表中每一行，即所有数据
        result = alldata[0]#取出表中第一列数据
        numbers.append(result)
    return numbers


inpath = 'all.xls'#基金项目文件所在路径
ns=extract(inpath)#基金号列表
use_list=[]#能够检索到的基金号列表
count_number=0
for i in ns:
    tiao=get_html(i,count_number)
    count_number=count_number+1
    if tiao=='下一个':
        continue
    else:
        use_list.append(i)

#将有效基金号存储为excel
f=xlwt.Workbook()
sheet1=f.add_sheet(u'sheet1',cell_overwrite_ok=True)
sheet1.write(0,0,'基金号')
i=1
for data in use_list:#遍历每一行
    for j in range(len(data)):#取每一单元格
        sheet1.write(i,j,data[j])#写入单元格
    i=i+1#往下一行
f.save('有效基金号.xls') 