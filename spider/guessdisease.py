from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 配置 Headless 模式
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://xiaoce.fun/guessdisease")

# 执行交互（示例：点击按钮）
button = driver.find_element_by_css_selector("button.start-challenge")
button.click()

# 提取纯文本结果（结合 w3m）
page_text = driver.page_source
with open("temp.html", "w") as f:
    f.write(page_text)
os.system("w3m -dump temp.html")  # 输出可读文本到终端

driver.quit()