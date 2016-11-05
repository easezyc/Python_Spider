# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 19:41:20 2016

@author: zhuyongchun
"""

import re
import urllib.request
import urllib
import os
#urlRoot = "http://202.112.88.39:8080/zyc/"  # the target website
#targetDir="./zyc/"
urlRoot="http://history.bnu.edu.cn/"
targetDir="./history/"
visited = set()
def getContent(cururl):
    req = urllib.request.Request(cururl,headers = {
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
            })
    page = urllib.request.urlopen(req)
    pageContent = page.read()
    return pageContent

def destFile(url):     #通过绝对路径计算出相对路径
    if not os.path.isdir(targetDir):  
        os.mkdir(targetDir)
    path=url[len(urlRoot):len(url)]
    pathlist=path.split('/')
    abpath=targetDir
    for tpath in pathlist[0:len(pathlist)-1]:
        abpath=os.path.join(abpath,tpath)
        if not os.path.isdir(abpath):
            os.mkdir(abpath)
    abpath=os.path.join(abpath,pathlist[len(pathlist)-1])
    return abpath

def trace(url,content,urllist):    #遍历
    allurl = re.compile(r'href="([^\s]*?((jsp)|html))"')
    UrlList = set(re.findall(allurl,str(content)))
    allNormalUrlList=getNormalUrlList(UrlList,url,urllist)
    urllist=urllist.extend(allNormalUrlList)
    return urllist
    
def getNormalUrlList(List,url,preurllist):    #计算出页面中包括的url并全部转换为绝对路径
    newList=[]
    for turl,x,y in List:
        if turl.startswith("http://",0,len(turl)):
            if turl.find(urlRoot,0,len(turl))==-1 and turl.find(urlRoot + '#',0,len(turl))==-1 and (turl not in visited) and (turl not in preurllist) and (turl not in newList):
                newList.append(turl) 
        else:
            newurl = urllib.parse.urljoin(url,turl)      
            if newurl not in visited and (newurl not in preurllist) and (newurl not in newList):               
                newList.append(newurl)
    return newList

def getImgs(Content,url,allimgList):
    reg = r'src="([^\s]*?(jpg|png|(gif)))"'
    imgre = re.compile(reg)
    imgList = re.findall(imgre,str(Content))
    sd_imgNewList = getNormalUrlList(imgList,url,allimgList)
    for sd_imgurl in sd_imgNewList:
        sd_imgPath = destFile(sd_imgurl)
        try:
            urllib.request.urlretrieve(sd_imgurl,sd_imgPath)
        except urllib.error.URLError:
            print("The image '",sd_imgurl,"' not Found.")
            
def getCss(Content,url,allcssList):
    reg = r'href="(([^\s]*)?(.css))"'
    cssre = re.compile(reg)
    cssList = re.findall(cssre,str(Content))
    sd_cssNewList = getNormalUrlList(cssList,url,allcssList)
    for sd_cssUrl in sd_cssNewList:
        sd_cssPath = destFile(sd_cssUrl)
        try:
            urllib.request.urlretrieve(sd_cssUrl,sd_cssPath)
        except urllib.error.HTTPError:
            print("The css file '",sd_cssUrl,"' not Found.") 
        
def getJs(Content,url,alljsList):
    reg = r'src="(([^\s]*)?(.js))"'
    jsre = re.compile(reg)
    jsList = re.findall(jsre,str(Content))
    sd_jsNewList = getNormalUrlList(jsList,url,alljsList)
    for sd_jsUrl in sd_jsNewList:
        sd_jsPath = destFile(sd_jsUrl)
        try:
            urllib.request.urlretrieve(sd_jsUrl,sd_jsPath)
        except urllib.error.HTTPError:
            print("The js file '",sd_jsUrl,"' not Found.") 
         
if __name__ == '__main__':
    urllist=[]
    allimgList=[] 
    allcssList=[]
    alljsList=[]
    pagenum=0
    firsturl=urlRoot+'index.html'
    urllist.append(firsturl)
    while len(urllist)>0:
        cururl=urllist.pop()
        visited |= {cururl}  # 标记为已加入队列 
        try:
            urllib.request.urlretrieve(cururl,destFile(cururl))
            pagenum=pagenum+1
            print("第",pagenum,"个页面:",cururl)
            curcontent=getContent(cururl)
            print(1)
            lastSplashPos = cururl.rindex('/')
            cururl = cururl[0:lastSplashPos+1]
            getImgs(curcontent,cururl,allimgList)
            print(2)
            getCss(curcontent,cururl,allcssList)
            print(3)
            getJs(curcontent,cururl,alljsList)
            print(4)
            trace(cururl,curcontent,urllist)
            print(5)
            #getHtmls()
        except urllib.error.URLError:
            print("The page '", cururl, "' not Found.")