# eelのインポート
import eel
import socket
import pandas as pd

# ウエブコンテンツを持つフォルダー
eel.init('web', allowed_extensions=['.js', '.html', '.css'])

CHROME_ARGS = [
    '--incognit',  # シークレットモード
    '--disable-http-cache',  # キャッシュ無効
    '--disable-plugins',  # プラグイン無効
    '--disable-extensions',  # 拡張機能無効
    '--disable-dev-tools',  # デベロッパーツールを無効にする
]
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

@eel.expose
def kimetsu_search(word,csv_name):
    # 検索対象取得
    df=pd.read_csv("./{}".format(csv_name))
    source=list(df["name"])

    # 検索
    if word in source:
        print("『{}』はいます".format(word))
        #eel.view_log_js("『{}』はいます".format(word))
    else:
        print("『{}』はありません".format(word))
        #eel.view_log_js("『{}』はいません".format(word))
        #eel.view_log_js("『{}』を追加します".format(word))
        # 追加
        #add_flg=input("追加登録しますか？(0:しない 1:する)　＞＞　")
        #if add_flg=="1":
        source.append(word)
    
    # CSV書き込み
    df=pd.DataFrame(source,columns=["name"])
    df.to_csv("./{}".format(csv_name),encoding="utf_8-sig")
    print(source)

eel.start('index.html', options=options, suppress_error=True)