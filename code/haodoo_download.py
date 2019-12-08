#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import io
import urllib
import urllib.request

# from fake_useragent import UserAgent

def storeContent(file_name, file_content, mode = "wt"):
    with open(file_name, mode) as f:
        f.write(file_content);
    return 0
    
class htmlDownLoad(object):
    def __init__(this, base_url):
        this.base_url_ = base_url
        if base_url and (not base_url.endswith('/')):
            this.base_url_.append('/')
        
    def doDownload(this, relative_url, convert_flg = True):
        if ((not this.base_url_) or (not relative_url)):
            return null
        
        full_url = this.base_url_ + relative_url
        response = urllib.request.urlopen(full_url)
        if (response is None):
            return null
            
        data = response.read();
        if (data is None):
            return null
            
        if (convert_flg):
            utf8_str = data.decode('utf-8');
            return utf8_str
        else:
            return data    

class bookInfo(object):
    def __init__(self):
        pass
    
class authorInfo:
    def __init__(self):
        self.books_ = []
        self.name_ = ''
    
def parseBookNames(data, start_index, author_info):
    book_ref_key1 = '?M=book&P='
    book_ref_key2 = '?M=Share&P='
    
    str_author_start = '<font color=\"CC0000\">'
    next_author_start = data.find(str_author_start, start_index)
    if (next_author_start > 0):
        index_find_end = next_author_start
    else:
        index_find_end = len(data)

    while (True):
        index1 = data.find(book_ref_key1, start_index, index_find_end)
        index2 = data.find(book_ref_key2, start_index, index_find_end)
        if ((index1 < 0) and (index2 < 0)):
            break
            
        if (index1 < 0):
            index = index2
        elif (index2 < 0):
            index = index1
        else:
            if (index1 < index2):
                index = index1
            else:
                index = index2                
        
        index2 = data.find('\">', index, index + 50)    
        if (index2 < 0):
            break
            
        sub_url = data[index : index2]
        index2 += 2
        index3 = data.find('</a>', index2, index_find_end)
        if (index3 < 0):
            break
            
        name = data[index2 : index3]
        # print('    sub-url: %s; name: %s' % (sub_url, name))
        start_index = index3 + len('</a>')
        
        book_info = bookInfo()
        book_info.sub_url_ = sub_url
        book_info.name_ = name
        author_info.books_.append(book_info)                

    if (next_author_start > 0):
        return next_author_start
        
    return -1    
                        
def downloadFile(downloadInstance, command_str, data_content, start_search_index, book_name, author_name, category_name):
    if (command_str == 'DownloadUpdb'):
        file_surfix = '.updb'
    elif (command_str == 'DownloadEpub'):
        file_surfix = '.epub'
    elif (command_str == 'DownloadVEpub'):
        file_surfix = '.epub'
    elif (command_str == 'DownloadMobi'):
        file_surfix = '.mobi' 
    else:
        return  # not supported    

    find_index = data_content.find(command_str, start_search_index)
    if (find_index < 0):
        return
        
    index1 = data_content.find('(\'', find_index + len(command_str))
    if (index1 < 0):
        return
        
    index2 = data_content.find('\')', index1 + 2)
    if (index2 < 0):
        return
    
    # 司/臥/獨/諸
    author_name = author_name.replace('/', '‧')
    download_file_name = data_content[index1 + 2 : index2]
    file_name = author_name + '_' + book_name + '_' + download_file_name + file_surfix
    
    cwd = os.getcwd()
    cur_path = os.path.join(cwd, category_name)
    if (not os.path.exists(cur_path)):
        os.mkdir(cur_path)
        
    full_file_path = os.path.join(cur_path, file_name)
    if (os.path.exists(full_file_path) and os.path.isfile(full_file_path)):
        print('file exists. ignore. file: ' + file_name)
        return
    
    book_name_sub_url = '?M=d&P='            
    book_name_sub_url += download_file_name
    book_name_sub_url += file_surfix
    download_data = downloadInstance.doDownload(book_name_sub_url, False)
    if (not download_data):
        return
        
    if (storeContent(full_file_path, download_data, 'wb') == 0):
        print('downloaded file: %s; length: %d' % (file_name, len(download_data)))
    return    
        
               
def parseBookContent(htmlData, book_name, author_name, category_name, downloadInstance):
    str_author_start = '<font color=\"CC0000\">'
    
    index = htmlData.find('<!--------------------- START INCLUDE FILES --------------------->')
    if (index < 0):
        index = htmlData.find('SetTitle')
    if (index < 0):
        return
    
    while (True):
        index1 = htmlData.find(str_author_start, index)
        if (index1 < index):
            break
            
        index1 += len(str_author_start)
        
        index2 = htmlData.find("</font>", index1)
        if (index2 < index1):
            break
            
        index2 += len('</font>')
        
        index3 = htmlData.find('<input type=\"button\"', index2)
        if (index3 < index2):
            break
            
        book_name = htmlData[index2 : index3]
        index3 += len('<input type=\"button\"')
        
        # print('book name: ' + book_name)
        downloadFile(downloadInstance, 'DownloadUpdb', htmlData, index3, book_name, author_name, category_name)
        downloadFile(downloadInstance, 'DownloadEpub', htmlData, index3, book_name, author_name, category_name)
        downloadFile(downloadInstance, 'DownloadVEpub', htmlData, index3, book_name, author_name, category_name)
        
        # uncomment this line if you want download mobi format as well
        downloadFile(downloadInstance, 'DownloadMobi', htmlData, index3, book_name, author_name, category_name)        
        
        index = index3
                    
    return
                
def parseParentContent(data):
    if (len(data) <= 0):
        return null
        
    author_list = []
    
    str_author_start = '<font color=\"CC0000\">'
    flg = True
    
    index = 0
    while (flg):
        index1 = data.find(str_author_start, index)
        if (index1 < 0):
            flg = False
            break
            
        index1 += len(str_author_start)    
        index2 = data.find('</font>', index1)
        if (index2 < 0):
            break

        # prepare for the next round of 
        index = index2 + len('</font>')  
        if ((index1 + 1) < index2):
            author_info = authorInfo()
            
            author_name = data[index1 : index2]
            index_tt = author_name.find('</')
            if (index_tt > 0):
                author_name = author_name[:index_tt]
            
            author_info.name_ = author_name
            index = parseBookNames(data, index, author_info)
            if (len(author_info.books_) > 0):
                author_list.append(author_info)
                
                print ('author: %s' % (data[index1 : index2]))
                for item in author_info.books_:
                    print('    sub-url: %s; name: %s' % (item.sub_url_, item.name_))
                                     
    return author_list  
    
#======================================================================================================================
#======================================================================================================================
if __name__ == '__main__':
    downloadInstance = htmlDownLoad('http://www.haodoo.net/')
            
    sub_url_list = ['?M=hd&P=100', '世紀百強', '?M=hd&P=wisdom', '隨身智囊', '?M=hd&P=history', '歷史煙雲', '?M=hd&P=martial', '武俠小說', '?M=hd&P=mystery', '懸疑小說', '?M=hd&P=romance', '言情小說', '?M=hd&P=scifi', '奇幻小說', '?M=hd&P=fiction', '小說園地']    
    # sub_url_list = ['?M=hd&P=martial', '武俠小說']    
    for index in range(0, len(sub_url_list), 2):
        sub_url = sub_url_list[index]
        print('index: %d; sub-url: %s; title: %s' % (index, sub_url, sub_url_list[index + 1]))
        file_name = sub_url_list[index + 1] + '.html'
        content = downloadInstance.doDownload(sub_url)
        if (not content):
            continue
            
        author_list = parseParentContent(content)
        for author_info in author_list:
            for book_info in author_info.books_:
                content = downloadInstance.doDownload(book_info.sub_url_)
                if (not content):
                    continue
                    
                parseBookContent(content, book_info.name_, author_info.name_, sub_url_list[index + 1], downloadInstance)    
        
    
        