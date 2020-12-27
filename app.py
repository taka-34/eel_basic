# eelのインポート
import eel
import socket
import pandas as pd
import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import datetime
from selenium.webdriver.common.action_chains import ActionChains


LOG_FILE_PATH = "./log/log_###DATETIME###.log"
log_file_path=LOG_FILE_PATH.replace("###DATETIME###",datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))



CHROME_ARGS = [
    '--incognit',  # シークレットモード
    '--disable-http-cache',  # キャッシュ無効
    '--disable-plugins',  # プラグイン無効
    '--disable-extensions',  # 拡張機能無効
    '--disable-dev-tools',  # デベロッパーツールを無効にする
]
ALLOW_EXTENSIONS = ['.html', '.css', '.js', '.ico']

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 0))
port = s.getsockname()[1]
s.close()

options = {
        'mode': "chrome",
        'close_callback': exit,
        'port': port,
        'cmdline_args': CHROME_ARGS
}
size=(700,600)

def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)

### ログファイルおよびコンソール出力
def log(txt):
    now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)


@eel.expose
def main(word,csv_name,check):
    if check:
        print("除外する")
    else:
        print("除外しない")

    log("処理開始")
    log("検索カテゴリ:{}".format(word))
    
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", True)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", True)
    
    #マウスオーバーを使うための宣言みたいなもの
    actions = ActionChains(driver)

    # Webサイトを開く
    driver.get("https://crowdworks.jp/public/jobs?category=jobs&order=score&ref=toppage_hedder")
    time.sleep(3)
    word_list = driver.find_elements_by_class_name("parent.cw-list_nav_subcategory_wrapper")

    scr = 20
    flg = False
    for w in word_list:
        
        driver.execute_script("window.scrollTo({}, {})".format(0,scr))
        scr += 15
        actions.move_to_element(w).perform()
        mini_cgr = w.find_elements_by_tag_name("a")
        for a in mini_cgr:
            if a.text == word:
                mini_cgr_url = a.get_attribute("href")
                flg = True
                break
        if flg:
            break
    
    

    try:
        driver.get(mini_cgr_url)
        time.sleep(3)
    except Exception as e:
        log("選択したカテゴリが見つかりません、終了します カテゴリ名: {}".format(word))
        eel.view_log_js("選択したカテゴリが見つかりません、終了します カテゴリ名: {}".format(word))
        log(e)
        return
    
    #募集終了案件を除外する
    if check:
        check_box = driver.find_element_by_class_name("filter.display-options")
        check_box.find_element_by_class_name("cw-checkbox_inline").click()
        time.sleep(3)

    name_list = []
    price_list = []
    suggest_list = []
    url_list = []
    timer_list = []
    count = 0
    success = 0
    fail = 0

    #次ページがなくなるまで探索
    while True:

        time.sleep(3)

        job_items = driver.find_elements_by_class_name("item_body.job_data_body")
        for job_item in job_items:
            try:
                name_a_url = job_item.find_element_by_class_name("item_title")
                job_name = name_a_url.find_element_by_tag_name("a")
                name_list.append(job_name.text)
                url_list.append(job_name.get_attribute("href"))

                price_list.append(job_item.find_element_by_class_name("entry_data.payment").text)
                suggest_list.append(job_item.find_element_by_class_name("entry_data.entries").text)
                timer_list.append(job_item.find_element_by_class_name("entry_data.expires").text)
                
                
                log("{}件目成功 : {}".format(count,job_name.text))
                eel.view_log_js("{}件目成功 : {}".format(count,job_name.text))
                success+=1
                print(job_name.text)
                    
            except Exception as e:
                log("{}件目失敗 : {}".format(count,job_name.text))
                eel.view_log_js("{}件目失敗 : {}".format(count,job_name.text))
                log(e)
                fail+=1
            finally:
                count+=1

        next_page = driver.find_elements_by_class_name("to_next_page")
        if len(next_page) >= 1:
            next_page_link = next_page[0].get_attribute("href")
            driver.get(next_page_link)
        else:
            log("最終ページです。終了します。")
            eel.view_log_js("最終ページです。終了します。")
            break
        
    #csvファイルに出力    
    df = pd.DataFrame({"案件名":name_list,
                       "価格":price_list,
                       "提案・契約数":suggest_list,
                       "残り時間":timer_list,
                       "URL":url_list})
    df.to_csv("{}".format(csv_name),encoding="utf_8-sig")
    log("処理完了 成功件数: {} 件 / 失敗件数: {} 件".format(success,fail))


eel.init('web',allowed_extensions=ALLOW_EXTENSIONS)
eel.start('index.html',options=options,size=size, suppress_error=True)
    

