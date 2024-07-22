import requests

class SecEdgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.tickerdict = {}
        self.get_data()


    def get_data(self):
        header = {'user-agent': 'MLT GS skelete@ucsc.edu'}
        data = requests.get(self.fileurl, headers=header)

        if data.raise_for_status:
            self.company_info = data.json()
            for info in self.company_info.values():
                cik = info['cik_str']
                ticker = info['ticker']
                title = info['title']

                if cik and ticker and title:
                    self.namedict[title.lower()] = (title,ticker,cik)
                    self.tickerdict[ticker.lower()] = (title,ticker,cik)
                else:
                    print("Incomplete data: {info}")
        else:
            print("Error fetching data, Status Code 200")

    def name_to_cik(self, title):
        return self.namedict.get(title.lower())

    def ticker_to_cik(self, ticker):
        return self.tickerdict.get(ticker.lower())

se = SecEdgar('https://www.sec.gov/files/company_tickers.json')

print(se.name_to_cik('MICROSOFT CORP'))
print(se.ticker_to_cik('NVDA'))
