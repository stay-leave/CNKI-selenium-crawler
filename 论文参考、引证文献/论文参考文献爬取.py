#coding='utf-8'
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time as t
import re
from bs4 import BeautifulSoup
import xlrd
import xlwt
import random
import os 

#删除英文期刊文献
#有时候是万方的，要注意，写个万方的
#每次返回的源码都不一样，需要重新返回新的
#知网点击下一页需要将页面元素拖入可见区域

#先进入浏览器知网
driver = webdriver.Firefox()
driver.minimize_window()

def go_zn():
    """翻到第二页及以后，返回所有期刊和题录信息"""
    target = driver.find_element_by_xpath('/html/body/div[1]/div[2]/span/a[2]')#定位到下一页区域
    driver.execute_script('arguments[0].scrollIntoView();', target) 
    t.sleep(2)
    nwepage = driver.find_element_by_partial_link_text('下一页')
    nwepage.click()#点击下一页
    t.sleep(5)
    html= driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    name_1=[]
    name=soup.select('html body.rootw div.essayBox ul.ebBd li a')#期刊
    clear(name,name_1)
    return name_1
def yin():
    """返回引证文献"""
    driver.switch_to.default_content()#跳出框架
    target = driver.find_element_by_xpath('//*[@id="rl3"]')
    driver.execute_script('arguments[0].scrollIntoView();', target) 
    driver.find_element_by_xpath('//*[@id="rl3"]').click()#点击引证文献
    t.sleep(5)
    driver.switch_to.frame("frame1")
    html_one= driver.page_source
    soup_one = BeautifulSoup(html_one,'html.parser')
    name_one=[]
    nameone=soup_one.select('html body.rootw div.essayBox ul.ebBd li a')#期刊（第二页)
    clear(nameone,name_one)
    return name_one
def list_of_groups(init_list, children_list_len):
    list_of_groups = zip(*(iter(init_list),) *children_list_len)
    end_list = [list(i) for i in list_of_groups]
    count = len(init_list) % children_list_len
    end_list.append(init_list[-count:]) if count !=0 else end_list
    return end_list
def clear(old_list,new_list):
        """用于清洗出纯文本"""
        for i in old_list:
            n=(i.text).strip()
            n=n.replace('\n',' ')
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
        result = alldata[8]#取出表中第一列数据
        numbers.append(result)
    return numbers
def extract_url(inpath):
    """取出知网链接"""
    data = xlrd.open_workbook(inpath, encoding_override='utf-8')
    table = data.sheets()[0]#选定表
    nrows = table.nrows#获取行号
    ncols = table.ncols#获取列号
    numbers_1=[]#url
    numbers_2=[]#lun
    for i in range(1, nrows):#第0行为表头
        alldata = table.row_values(i)#循环输出excel表中每一行，即所有数据
        result = alldata[6]#取出表中第一列数据
        numbers_1.append(result)
    for i in range(1, nrows):#第0行为表头
        alldata = table.row_values(i)#循环输出excel表中每一行，即所有数据
        result = alldata[0]#取出表中第一列数据
        numbers_2.append(result)
    return numbers_1,numbers_2
def save_afile(alls,alls_y,num,lun):
    """将一个论文的所有参考文献和被引文献保存在一个excel
        第一个是中文参考期刊，第二个是中文被引期刊，第三个是基金号
        以一个基金号为单位保存该基金号下所有参考文献和被引文献
    """
    if os.path.exists('F:\图情社科基金项目数据爬取\论文信息-参考文献'+'\\'+str(num)):
        print('yes')
    else:
        os.makedirs('F:\图情社科基金项目数据爬取\论文信息-参考文献'+'\\'+str(num))
    os.chdir('F:\图情社科基金项目数据爬取\论文信息-参考文献'+'\\'+str(num))#进入参考文献的基金文件夹
    f=xlwt.Workbook()
    sheet1=f.add_sheet(u'参考文献',cell_overwrite_ok=True)
    sheet1.write(0,0,'论文名称')
    sheet1.write(0,1,'发表期刊')
    sheet1.write(0,2,'发表时间')
    i=1
    #for all in alls:#遍历每一页
    for data in alls:#遍历每一行
        for j in range(len(data)):#取每一单元格
            sheet1.write(i,j,data[j])#写入单元格
        i=i+1#往下一行
    sheet2=f.add_sheet(u'引证文献',cell_overwrite_ok=True)
    sheet2.write(0,0,'论文名称')
    sheet2.write(0,1,'发表期刊')
    sheet2.write(0,2,'发表时间')
    n=1
    #for all in alls_y:
    for data in alls_y:#遍历每一行
        for j in range(len(data)):#取每一单元格
            sheet2.write(n,j,data[j])#写入单元格
        n=n+1#往下一行
    #os.chdir('F:\图情社科基金项目数据爬取\参考文献')
    f.save(str(lun)+'.xls')
    
def get(url):
    """进入知网链接
          最终返回中文参考文献和被引文献
    """
    driver.get(url)#进入论文详情页
    t.sleep(random.randint(3, 9))
    try:
        driver.switch_to.frame("frame1")
    except:
        pass
    html_now= driver.page_source#详情首页面源码
    soup_1= BeautifulSoup(html_now,'html.parser')    #解析器：html.parser
    try:
        cou_p=soup_1.select('html body.rootw div.essayBox div.dbTitle b.titleTotle span#pc_CJFQ')#中文期刊总数
        cou_p=int(cou_p[0].text)
    except:
        cou_p=0

    cou_p_a=cou_p*3#中文期刊未切分总数，由于中文一个有三个子属性
    page_p=float(float(cou_p)/10)
    ac=int(float(cou_p)/10)
    if page_p!=ac:#奇数
        page_p=ac+1#总共的中文期刊页数
    else:
        page_p=ac

    can_zn=[]#中文参考期刊
    yinz=[]#引证文献


    while True:
        if page_p==0:
            break
        elif page_p==1:#中文期刊不超过一页
            name_l_1=[]
            name_l=soup_1.select('html body.rootw div.essayBox ul.ebBd li a')#获得当前页面所有的期刊和题录
            clear(name_l,name_l_1)
            can_zn.append(name_l_1[:cou_p_a])#注意中文期刊有三个属性：题名、期刊、时间
            yinz=yin()
            break
        else:#中文期刊超过一页
            name_l_1=[]
            name_l=soup_1.select('html body.rootw div.essayBox ul.ebBd li a')#获得当前页面所有的期刊和题录
            clear(name_l,name_l_1)
            can_zn.append(name_l_1[:30])#注意中文期刊有三个属性：题名、期刊、时间
            #以上是第一页
            count=1
            for i in range(page_p-1):
                t.sleep(random.randint(3, 5))
                name=go_zn()
                count=count+1
                if count==page_p:#到了最后一页
                    can_zn.append(name[:cou_p_a-((page_p-1)*30)])
                else:
                    can_zn.append(name[:30])#注意中文期刊有三个属性：题名、期刊、时间
            yinz=yin()
            break
     #划分为小列表
    #将列表降维
    #把列表转为字符串
    b = str(can_zn)
    #替换掉'['和']'
    b = b.replace('[','')
    b = b.replace(']','')
    b=b.strip()
    #最后转化成列表
    try:
        can_zn= list(eval(b))
    except:
        can_zn=[]
    can_cn=list_of_groups(can_zn,3)
    yin_z=list_of_groups(yinz,3)#正常
    return can_cn,yin_z
#知网
jijin=extract('基金号列表.xls')#取出基金号列表
for i in jijin[1408:1409]:#遍历
    i='14BTQ073'
    try:
        url_s,lun_s=extract_url('F:\图情社科基金项目数据爬取\论文信息\\'+str(i)+'.xls')#打开每个基金号论文信息的xls文件
        print('获取到'+str(i)+'的论文网址及题目')
    except:
        print(str(i)+'基金号无产出论文，跳过')
        continue
    for u,l in zip(url_s,lun_s):
        l=re.sub(r'[^\u4e00-\u9fa5]','',str(l))#保证只有中文
        if u==0:
            continue
        else:
            t.sleep(2)
            can_cn,yin_z=get(str(u))#进入一个论文的详情链接
            t.sleep(5)
            save_afile(can_cn,yin_z,i,l)
            print(str(l)+'的参考、引证文献获取完毕')
    print(str(i)+'的所有论文的参考、引证文献获取完毕')

driver.quit()
#print('结束！')
#只能获取期刊文献，对于引证的硕士毕业论文等，排版会有偏差。
#这是因为无法获取到非期刊文献的出版时间，导致第二个文献的题名被填充到了第一个的出版时间的位置
#懒得改了，可以把它们删除，只关注期刊文献
  



    















                                                         












