from flask import Flask, request, jsonify
from index import scrape_urls

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape_api():
    """
    スクレイピングAPIエンドポイント。

    クエリパラメータ:
        itemId (str): 抽出対象のアイテムID (例: J0000037910)。

    レスポンス:
        JSON形式でスクレイピングデータを返します。
    """
    item_id = request.args.get('itemId')
    if not item_id:
        return jsonify({'error': 'itemId パラメータが必要です。'}), 400

    output_html = f'data/fetched_{item_id}.html'
    rankings_csv = f'data/top10_rankings_{item_id}.csv'

    rankings = scrape_urls(item_id, output_html, rankings_csv)
    if rankings is None:
        return jsonify({'error': 'データの取得に失敗しました。'}), 500

    if not rankings:
        return jsonify({'message': 'ランキング情報が存在しません。'}), 404

    return jsonify({'rankings': rankings}), 200

def main():
    """
    Flaskアプリケーションを実行します。
    """
    app.run(host='0.0.0.0', port=5001, debug=True)

if __name__ == "__main__":
    main()