#coding='utf-8'
import requests
import re
import xlwt

headers = {
				  'Accept-Encoding': 'gzip, deflate, sdch',
				 'Accept-Language': 'en-US,en;q=0.8',
				 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				 'Referer': 'https://www.baidu.com/',
			    'Connection': 'keep-alive',
				}

url_1='http://fz.people.com.cn/skygb/sk/index.php/index/seach/'
url_2='?pznum=&xmtype=0&xktype=%E5%9B%BE%E4%B9%A6%E9%A6%86%E3%80%81%E6%83%85%E6%8A%A5%E4%B8%8E%E6%96%87%E7%8C%AE%E5%AD%A6&xmname=&lxtime=0&xmleader=&zyzw=0&gzdw=&dwtype=0&szdq=0&ssxt=0&cgname=&cgxs=0&cglevel=0&jxdata=0&jxnum=&cbs=&cbdate=0&zz=&hj='#学科类别，这里是图情
url_0=list(range(1,94))#生成一个1到93的数字列表，要看需要爬取的基金学科共有多少页。
urls=[]#网址列表

def require(url):
	"""获取网页源码
	"""
	response = requests.get(url, headers=headers)
	print(response.status_code)#状态码
	#print(response.encoding)首选编码
	'''
	print(response.apparent_encoding)#备选编码
	response.encoding=response.apparent_encoding
	'''
	html=response.text#源代码文本
	return html
def cut(list,n):
	"""将列表按特定数量切分成小列表"""
	for i in range(0,len(list),n):
		yield list[i:i+n]
for i in url_0:
	i=url_1+str(i)+url_2
	urls.append(i)#网址列表
def get_infor(one_url):
	'''进入一个页面，获取该页面的信息，返回列表的列表all'''
	html=require(one_url)
	result_1=re.findall('<table width="100%" border="0" cellpadding="0" cellspacing="0">(.*?)</table>',html,re.S)#进入table
	result_2=re.findall(' <tr>(.*?)</tr>',str(result_1),re.S)#找到所有tr标签，行

	#项目编号、立项时间、项目负责人、所属系统
	i_1=re.findall('<td width="90">(.*?)</td>',str(result_2),re.S)#找到所有td width=90的标签,得出四种不同的属性，项目编号、立项时间、项目负责人、所属系统
	i_2=re.findall('<span title.*?>(.*?)</span>',str(i_1),re.S)#取出字符,i_2是一个列表
	#项目类别、学科分类、专业职务
	i_3=re.findall('<td width="70">(.*?)</td>',str(result_2),re.S)#找到所有td width=70的标签,得出三种不同的属性，项目类别、学科分类、专业职务
	i_4=re.findall('<span title.*?>(.*?)</span>',str(i_3),re.S)#取出字符
	#项目名称
	i_5=re.findall('<td width="320"><span.*?>(.*?)</span></td>',str(result_2),re.S)#找到所有td width=320的标签,得出项目名称
	#工作单位
	i_6=re.findall('<td width="150"><span.*?>(.*?)</span></td>',str(result_2),re.S)#找到所有td width=150的标签,得出工作单位
	#单位类别
	i_7=re.findall('<td width="80"><span.*?>(.*?)</span></td>',str(result_2),re.S)#找到所有td width=80的标签,得出单位类别
	#所在地
	i_8=re.findall('<td width="100"><span.*?>(.*?)</span></td>',str(result_2),re.S)#找到所有td width=100的标签,得出所在省市区

	l_1=[]
	l_2=[]
	for i in cut(i_2,4):#四种属性的值列表
		l_1.append(i)

	for i in cut(i_4,3):#三种属性的值列表
		l_2.append(i)

	all=[]#总的结果
	#列表拼接
	for i in range(len(i_8)):
		all.append(l_1[i]+l_2[i]+i_5[i:i+1]+i_6[i:i+1]+i_7[i:i+1]+i_8[i:i+1])
	return all


"""保存为excel"""
f=xlwt.Workbook()
sheet1=f.add_sheet(u'sheet1',cell_overwrite_ok=True)
sheet1.write(0,0,'项目编号')
sheet1.write(0,1,'立项时间')
sheet1.write(0,2,'项目负责人')
sheet1.write(0,3,'所属系统')
sheet1.write(0,4,'项目类别')
sheet1.write(0,5,'学科分类')
sheet1.write(0,6,'专业职务')
sheet1.write(0,7,'项目名称')
sheet1.write(0,8,'工作单位')
sheet1.write(0,9,'单位类别')
sheet1.write(0,10,'所在地')

i=1
alls=[]
for one_url in urls:
	alls.append(get_infor(one_url))#全部页的数据分为一个93个子列表的列表

for all in alls:#遍历每一页
	for data in all:#遍历每一行
		for j in range(len(data)):#取每一单元格
			sheet1.write(i,j,data[j])#写入单元格
		i=i+1#往下一行
f.save('测试文件.xls')#基金数据存储文件
#保存所有	
