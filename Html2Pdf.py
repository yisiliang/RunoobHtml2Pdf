import os
import gzip
import pdfkit
from urllib import request
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger, PdfFileReader


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


def save_to_pdf(url: str):
    print(url)
    pdf_name = url.split('/')[-1]
    pdf_name = pdf_name.split('.')[0]
    pdf_name = pdf_name + '.pdf'


    html = get_content_from_url(url)
    soup = BeautifulSoup(html, 'lxml')
    csshtml = ''
    for link in soup.find_all('link'):
        if link.get('type') == 'text/css':
            csshtml = csshtml + get_content_from_url(baseurl + link.get('href'))

    new_style_tag = soup.new_tag('style')

    new_style_tag.append(csshtml)
    head = soup.head.insert(0, new_style_tag)

    soup = remove_tag(soup, 'script')
    soup = remove_tag(soup, 'img')
    soup = remove_tag(soup, 'link')

    soup = remove_selector(soup, 'body > div.container.logo-search')
    soup = remove_selector(soup, 'body > div.container.navigation')
    soup = remove_selector(soup, 'body > div.container.main > div > div.col.left-column')
    soup = remove_selector(soup, 'body > div.container.main > div > div.fivecol.last.right-column')
    soup = remove_selector(soup, '#footer')
    soup = remove_selector(soup, '#htmlfeedback-container')
    soup = remove_selector(soup, 'body > div.fixed-btn')
    soup = remove_selector(soup, '#respond')
    soup = remove_selector(soup, '#comments')
    soup = remove_selector(soup, '#postcomments')
    soup = remove_selector(soup, 'body > div.container.main > div > div > div > div.article-heading-ad')
    soup = remove_selector(soup, 'body > div.cd-user-modal')

    soup = remove_selector_all(soup, '.previous-next-links')

    main_element = soup.select_one('body > div.container.main > div > div')

    main_element.attrs['style'] = 'width: 100%;'

    for ele in soup.find_all():
        ele.attrs['style'] = 'font-size:30pt;'

    html = str(soup)

    options = {
        'page-size': 'A4',
        'encoding': "UTF-8",
        'dpi': 300,
        'footer-center': url,
        'header-center': baseurl,
        'footer-font-size': 8,
        'header-font-size': 8,
    }

    pdfkit.from_string(html, pdf_name, options=options)
    print(pdf_name)
    return pdf_name


baseurl = 'http://www.runoob.com/'
book_name = 'angularjs'

start_url = 'http://www.runoob.com/'  + book_name + '/'  + book_name + '-tutorial.html'

html = get_content_from_url(start_url)
soup = BeautifulSoup(html, 'lxml')

urls_element = soup.select_one('#leftcolumn')

merger = PdfFileMerger()

for link in urls_element.find_all('a'):
    href = link.get('href')
    if href[0] != '/':
        href = '/' + book_name + '/' + href
    url = baseurl + href
    title = link.get('title')

    pdf_name = save_to_pdf(url)
    file = open(pdf_name, 'rb')
    merger.append(PdfFileReader(file), bookmark=title, import_bookmarks=False)
    file.close()
    os.remove(pdf_name)

merger.write(book_name + '.pdf')




