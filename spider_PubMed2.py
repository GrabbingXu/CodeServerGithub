import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import random
from functools import wraps
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# ========== 配置项 ==========
MAX_RETRIES = 3  # 单次请求最大重试次数
DELAY_RANGE = (0.1, 1.0)  # 随机延迟范围（秒）
THREADS = 2  # 线程数（根据CPU配置建议2-4）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ========== 重试装饰器 ==========
def retry_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                time.sleep(random.uniform(*DELAY_RANGE))  # 随机延迟
                return func(*args, **kwargs)
            except (requests.ConnectionError, requests.Timeout) as e:
                print(f"请求失败: {e}, 第{retries+1}次重试...")
                retries += 1
        print(f"请求失败超过最大重试次数 {MAX_RETRIES}, 跳过当前任务")
        return None
    return wrapper

# ========== 安全请求会话 ==========
session = requests.Session()
retry_strategy = Retry(
    total=MAX_RETRIES,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount('https://', HTTPAdapter(max_retries=retry_strategy))

# ========== 核心函数 ==========
@retry_request
def fetch_page(url):
    return session.get(url, headers=HEADERS, timeout=10)

def parse_list_page(html, keyword, page):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='docsum-content')
    return [process_item(item, keyword, page) for item in items]

def process_item(item, keyword, page):
    try:
        title_link = item.find('a', class_='docsum-title')
        title = title_link.text.strip() if title_link else "无标题"
        pmid_link = title_link.get('href', '') if title_link else ""
        return {'title': title, 'pmid_link': pmid_link}
    except Exception as e:
        print(f"页面解析失败（关键词:{keyword} 页:{page}）: {str(e)}")
        return None

@retry_request
def fetch_detail(pmid_link):
    detail_url = f'https://pubmed.ncbi.nlm.nih.gov{pmid_link}'
    response = session.get(detail_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    abstract = soup.find('div', class_='abstract-content selected')
    return abstract.text.strip() if abstract else "无法获得该篇摘要"

# ========== 多线程控制器 ==========
def main_controller(keyword, pages):
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        for page in range(1, pages + 1):
            url = f'https://pubmed.ncbi.nlm.nih.gov/?term={keyword}&page={page}'
            futures.append(executor.submit(process_page, url, keyword, page))
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                for idx, item in enumerate(result, 1):
                    print(
                        f"第{item['global_count']}篇 标题: {item['title']}\n"
                        f"链接: {item['detail_url']}\n"
                        f"PMID: {item['pmid_link']}\n"
                        f"摘要: {item['abstract']}\n"
                        f"{"-"*50}\n"
                        )

def process_page(url, keyword, page):
    response = fetch_page(url)
    if not response or response.status_code != 200:
        print(f"列表页获取失败（页:{page}）")
        return []
    
    items = parse_list_page(response.content, keyword, page)
    valid_items = [item for item in items if item and item['pmid_link']]
    
    # 获取详情页（二次多线程）
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        detail_futures = [executor.submit(fetch_detail, item['pmid_link']) for item in valid_items]
        for idx, future in enumerate(detail_futures):
            valid_items[idx]['abstract'] = future.result()
            valid_items[idx]['detail_url'] = f'https://pubmed.ncbi.nlm.nih.gov{valid_items[idx]["pmid_link"]}'
            valid_items[idx]['global_count'] = (page - 1) * len(valid_items) + idx + 1
    
    return valid_items

# ========== 用户交互 ==========
if __name__ == "__main__":
    # keyword = input('请输入搜索关键词（英文）: ')
    # pages = int(input('请输入要爬取的页数: '))
    keyword = 'breakfast skipping'
    pages = 399
    main_controller(keyword, pages)