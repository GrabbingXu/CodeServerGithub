import requests
from bs4 import BeautifulSoup

# 关键词 = input('请输入你想要搜索的英文关键词，按回车结束：')
# 页数 = input('请输入你想看到的页数，按回车结束：')
关键词 = 'breakfast skipping'
页数 = 399

g = 1

for j in range(1, int(页数) + 1):
    网址 = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + 关键词 + '&page=' + str(j)
    获取网址 = requests.get(网址)
    解析器 = BeautifulSoup(获取网址.content, 'html.parser')
    内容 = 解析器.find_all('div', class_='docsum-content')
    for i in 内容:
        标题链接 = i.find('a', class_='docsum-title')
        if 标题链接 is None:
            continue
        标题 = 标题链接.text.strip()
        PMID链接 = 标题链接['href']
        详细网址 = 'https://pubmed.ncbi.nlm.nih.gov' + PMID链接
        详细 = requests.get(详细网址)
        解析器2 = BeautifulSoup(详细.content, 'html.parser')
        摘要链接 = 解析器2.find('div', class_='abstract-content selected')
        if 摘要链接 is None:
            摘要 = '无法获得该篇摘要'
        else:
            摘要 = 摘要链接.text.strip()
        print('第' + str(g) + '篇 标题是：' + 标题 + '\n' + 详细网址 + '\n' + 'PMID:' + PMID链接 + '\n' + 摘要 + '\n' + '\n')
        g += 1