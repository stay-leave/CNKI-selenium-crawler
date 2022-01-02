# CNKI-selenium-crawler

配置：

本项目使用selenium模块，浏览器使用的是火狐。

1.下载geckodriver，地址https://github.com/mozilla/geckodriver/releases

2.将适配的安装包放置在火狐浏览器的安装路径、Python的Stricpts文件夹

3.将火狐的安装路径添加到电脑环境变量的用户变量的path中。


功能：

1.社科基金项目数据爬取

![image](https://user-images.githubusercontent.com/58450966/147872275-cee01300-9015-46a6-9d01-a677ce52d0ba.png)

2.论文的元数据爬取

![image](https://user-images.githubusercontent.com/58450966/147872625-67bcce52-79f7-44db-8114-9b7fabcff348.png)

3.论文的参考和引证的期刊文献爬取

参考文献
![image](https://user-images.githubusercontent.com/58450966/147872655-c36d6ac9-3e47-45d7-beae-f9d18583cf47.png)

引证文献
![image](https://user-images.githubusercontent.com/58450966/147872665-bd696b0d-7703-4e9c-8e25-16bad899eab3.png)

注意事项：

1.任意网络均适用，不需要购买知网。

2.可以按原始代码从社科基金项目开始直到产出论文的参考、引证文献的爬取。也可以自定义。

3.爬取速度可以调节，修改程序里的t.sleep()中的数值即可，建议1到6之间，可以采用random随机。

4.论文元数据爬取需要严格按照三个程序的顺序，即题名等、被引数等、论文地址。

5.所有结果均以excel方式保存，注意看文件路径。本项目中基金号为主键。

6.仅作学习使用。

