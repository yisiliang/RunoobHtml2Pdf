import os
import gzip
import pdfkit
import cssutils
from urllib import request
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger, PdfFileReader

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def get_content_from_url(url):
    try:
        rsp = request.urlopen(url)
    except:
        return ''

    if(rsp.info().get('Content-Encoding') == 'gzip'):
        try:
            html = gzip.decompress(rsp.read()).decode("utf-8")
        except:
            html = rsp.read().decode("utf-8")

    else:
        html = rsp.read().decode("utf-8")

    return html


def remove_tag(soup, tag_name):
    for tag in soup.find_all(tag_name):
        tag.extract()

    return soup


def remove_selector(soup, selector):
    element = soup.select_one(selector)
    if element is not None:
        element.extract()
    return soup


def remove_selector_all(soup, selector):
    for ele in soup.select(selector):
        ele.extract()
    return soup

def remove_font_rule(sheet):
    sheet_out = cssutils.parseString('')

    for rule in sheet:
        if rule.type != rule.FONT_FACE_RULE:
            sheet_out.add(rule)

    return sheet_out

def save_to_pdf(url: str, pdf_name: str):    

    soup_out = BeautifulSoup('<html><head><meta charset="utf-8"></head><body></body></html>', 'lxml')
    html = get_content_from_url(url)
    soup_in = BeautifulSoup(html, 'lxml')
    csshtml = ''
    for link in soup_in.find_all('link'):
        if link.get('href').endswith('.css'):
            css_url = baseurl + link.get('href')
            if css_dict.get(css_url) != None:
                csshtml = csshtml + css_dict[css_url]
            else:
                tmp_csshtml = get_content_from_url(css_url)
                sheet = cssutils.parseString(tmp_csshtml)
                sheet_out = remove_font_rule(sheet)
                tmp_csshtml = str(sheet_out.cssText, 'utf-8')
                css_dict[css_url] = tmp_csshtml
                csshtml = csshtml + css_dict[css_url]

    new_style_tag = soup_out.new_tag('style')
    new_style_tag.append(csshtml)
    soup_out.head.insert(0, new_style_tag)

    markdown_tags = soup_in.select('.content')
    i = 0;
    for markdown_tag in markdown_tags:
        markdown_tag['style'] = 'font-size:30pt;'
        soup_out.body.insert(i, markdown_tag)
        i = i+1

    soup_out = remove_tag(soup_out, 'script')
    soup_out = remove_tag(soup_out, 'img')
    soup_out = remove_tag(soup_out, 'iframe')
    html = str(soup_out)

    options = {
        'page-size': 'A4',
        'encoding': "UTF-8",
        'dpi': 300,
        'footer-center': url,
        'header-center': baseurl,
        'footer-font-size': 8,
        'header-font-size': 8,
    }
    try:
        pdfkit.from_string(html, pdf_name, options=options)
    except IOError as e:
        print(html)
        print(e)

    return pdf_name

build_path = 'build/'

isExists=os.path.exists(build_path)

# 判断结果
if not isExists:
    # 如果不存在则创建目录
    # 创建目录操作函数
    os.makedirs(build_path) 


baseurl = 'https://cn.vuejs.org/'
book_name = 'vuejs2'

css_dict = {};


html = get_content_from_url(baseurl + 'v2/guide/')
soup = BeautifulSoup(html, 'lxml')

#获取class为chapter的元素中的tag为a的元素列表
#cn.vuejs.org的章节为css类为sidebar-link
urls_element = soup.select('.sidebar-link')

merger = PdfFileMerger()

curEle=1;
for link in urls_element:
    href = link.get('href')

    url = baseurl + href
    title = link.getText().strip()
    tmp_pdf_name = 'tmp.pdf'
    save_to_pdf(url, tmp_pdf_name)
    file = open(tmp_pdf_name, 'rb')
    merger.append(PdfFileReader(file), bookmark=title, import_bookmarks=False)
    file.close()
    os.remove(tmp_pdf_name)
    print(str(curEle) + '/' + str(len(urls_element)))
    curEle = curEle + 1

merger.write(build_path + book_name + '.pdf')




