import requests

#retrieves data from the U.S. Securities and Exchange Commission (SEC) and returns a company's CIK
class SecEdgar:
    #initializes all variables needed for retrieving information
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.tickerdict = {}
        self.get_data()

    #function to retrieve and organize information into their respective dictionaries for organization
    def get_data(self):
        header = {'user-agent': 'MLT GS skelete@ucsc.edu'} #requested by the SEC website in order to gain authorization
        data = requests.get(self.fileurl, headers=header) #gets the information from the json file, with our header as a parameter

        if data.raise_for_status: # if the status code is 200, we have succesfully gained access
            self.company_info = data.json()
            for info in self.company_info.values(): #iterate through all company information
                #sets the information to a local variable
                cik = info['cik_str'] 
                ticker = info['ticker']
                title = info['title']

                if cik and ticker and title: #if all information has been set, add the company to the dictionary
                    self.namedict[title.lower()] = (title,ticker,cik)
                    self.tickerdict[ticker.lower()] = (title,ticker,cik)
                else: # else, company information is incomplete
                    print("Incomplete data: {info}")
        else: # status code is NOT 200, we have not succesfully gained access
            print("Error fetching data, Status Code 200")

    def name_to_cik(self, title): # returns cik from name
        return self.namedict.get(title.lower())

    def ticker_to_cik(self, ticker): # returns cik from ticker
        return self.tickerdict.get(ticker.lower())

se = SecEdgar('https://www.sec.gov/files/company_tickers.json')

print(se.name_to_cik('MICROSOFT CORP'))
print(se.ticker_to_cik('NVDA'))
