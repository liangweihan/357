from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def scrape_stock_data(stock_code):
    url = f'https://tw.stock.yahoo.com/quote/{stock_code}.TW/dividend'
    response = requests.get(url)

    try:
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        times = soup.find_all("div", class_="D(f) Start(0) H(100%) Ai(c) Bgc(#fff) table-row:h_Bgc(#e7f3ff) Pstart(12px) Pend(12px) Bdrststart(4px) Bdrsbstart(4px) Pos(r) Bxz(bb) Z(2)")
        dividend_periods = [time.text for time in times[:5]] if times else []

        moneys = soup.find_all("div", class_="Fxg(1) Fxs(1) Fxb(0%) Ta(end) Mend($m-table-cell-space) Mend(0):lc Miw(62px)")
        cash_dividends = [float(money.text) for index, money in enumerate(moneys[2:], start=1) if index % 2 != 0][:5] if moneys else []

        # 新增計算便宜價、合理價和昂貴價
        cheap_price = round((sum(cash_dividends) * 20) / 7, 2)
        fair_price = round((sum(cash_dividends) * 20) / 5, 2)
        expensive_price = round((sum(cash_dividends) * 20) / 3, 2)

        data = {
            'dividend_periods': dividend_periods,
            'cash_dividends': cash_dividends,
            'cheap_price': cheap_price,
            'fair_price': fair_price,
            'expensive_price': expensive_price
        }

        return {'success': True, 'data': data}

    except requests.RequestException as e:
        return {'success': False, 'message': f'Request failed: {e}'}

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    stock_code = request.json.get('stockCode')
    stock_data = scrape_stock_data(stock_code)
    return jsonify(stock_data)

if __name__ == '__main__':
    app.run(debug=True)  # 運行在本地的 127.0.0.1:5000