import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def fetch_html(target_url, headers):
    """
    指定されたURLからHTMLコンテンツを取得します。

    Args:
        target_url (str): 取得対象のURL。
        headers (dict): リクエストヘッダー。

    Returns:
        BeautifulSoup: パースされたHTMLコンテンツ。
    """
    try:
        response = requests.get(target_url, headers=headers)
        # エンコーディングの自動検出を有効にする
        response.encoding = response.apparent_encoding
        print(f"Detected encoding: {response.encoding}")
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data from {target_url}: {e}")
        return None

def save_to_csv(data, filepath):
    """
    データをCSVファイルに保存します。

    Args:
        data (list or dict): 保存するデータ。
        filepath (str): 保存先のCSVファイルのパス。
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        raise ValueError("保存するデータはリストまたは辞書形式である必要があります。")

    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"データが '{filepath}' に保存されました。")

def save_html(soup, filepath):
    """
    HTMLコンテンツをファイルに保存します。

    Args:
        soup (BeautifulSoup): パースされたHTMLコンテンツ。
        filepath (str): 保存先のHTMLファイルのパス。
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    print(f"HTMLが '{filepath}' に保存されました。" )

def get_header_text(soup):
    header = soup.find('h1')
    header_text = header.get_text(strip=True) if header else 'ヘッダー情報なし'
    return header_text

def extract_rankings(soup, top_n=20):
    """
    HTMLコンテンツからトップNのランキング情報を抽出します。

    Args:
        soup (BeautifulSoup): パースされたHTMLコンテンツ。
        base_domain (str): 抽出対象のベースドメイン。
        top_n (int, optional): 抽出するランキングの数。デフォルトは10。

    Returns:
        list: ランキング情報のリスト。
    """
    rankings = []
    ranking_sections = soup.find_all('span', class_='p-PTRank')

    if not ranking_sections:
        print("ランキングリストが見つかりませんでした。")
        return rankings

    # ヘッダー情報の取得
    header_text = get_header_text(soup)

    for rank_section in ranking_sections[:top_n]:
        parent_tr = rank_section.find_parent('tr')
        if not parent_tr:
            continue

        # 順位の抽出
        rank_number_tag = parent_tr.find('span', class_='p-PTRank')
        rank_number_text = rank_number_tag.get_text(strip=True)

        # 価格情報の抽出
        price_tag = parent_tr.find('p', class_='p-PTPrice_price')
        price_sub_tag = parent_tr.find('p', class_='p-PTPrice_sub')
        price_sub_tag_text = price_sub_tag.get_text(strip=True) if price_sub_tag else ''
        price_text = f"{price_tag.get_text(strip=True)}{price_sub_tag_text}" if price_tag and price_sub_tag else '価格情報なし'

        # 配送情報の抽出
        shipping_tag = parent_tr.find('button', class_='p-PTShipping_btn')
        shipping_text = shipping_tag.get_text(strip=True) if shipping_tag else '配送情報なし'

        # 在庫情報の抽出
        stock_tag = parent_tr.find('p', class_='p-PTStock')
        stock_text = stock_tag.get_text(strip=True) if stock_tag else '在庫情報なし'

        # ショップ情報の抽出
        shop_tag = parent_tr.find('a', class_='p-PTShopData_name_link')
        shop_name = shop_tag.get_text(strip=True) if shop_tag else 'ショップ名なし'
        shop_url = shop_tag['href'] if shop_tag and shop_tag.has_attr('href') else 'URLなし'

        # ショップエリアの抽出
        shop_area_tag = parent_tr.find('span', class_='p-PTShopData_name_area')
        shop_area_text = shop_area_tag.get_text(strip=True) if shop_area_tag else 'エリア情報なし'

        rankings.append({
            'Header': header_text,
            'Rank': rank_number_text,
            'Price': price_text,
            'Shipping': shipping_text,
            'Stock': stock_text,
            'Shop Name': shop_name,
            'Shop URL': shop_url,
            'Shop Area': shop_area_text
        })

    return rankings

def scrape_urls(target_url, output_html, rankings_csv):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    # HTMLの取得
    soup = fetch_html(target_url, headers)
    if soup is None:
        return

    # HTMLの保存
    save_html(soup, output_html)

    # ランキング情報の抽出
    rankings = extract_rankings(soup)
    if rankings:
        save_to_csv(rankings, rankings_csv)
    else:
        print("ランキング情報が存在しませんでした。")

def main():
    target_url = 'https://kakaku.com/item/J0000037910/'  # 抽出対象のURL
    output_html = 'data/fetched.html'  # 出力HTMLファイルのパス
    rankings_csv = 'data/top10_rankings.csv'  # トップ10ランキングの出力CSVファイルのパス

    scrape_urls(target_url, output_html, rankings_csv)

# def main():
#     """
#     Flaskアプリケーションを実行します。
#     """
#     app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()