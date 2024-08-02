import requests

#retrieves data from the U.S. Securities and Exchange Commission (SEC) and returns a company's CIK
class SecEdgar:
    #initializes all variables needed for retrieving information
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.cikdict = {}
        self.tickerdict = {}
        self.filingsdict = {}
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
                name = info['title']

                if len(str(cik)) < 9:
                    cikstr = str(cik)
                    cik = cikstr.zfill(10)

                if cik and ticker and name: #if all information has been set, add the company to the dictionary
                    self.namedict[name.lower()] = (name,ticker,cik)
                    self.tickerdict[ticker.lower()] = (name,ticker,cik)
                    self.cikdict[cik] = (name,ticker,cik)

                else: # else, company information is incomplete
                    print("Incomplete data: {info}")
        else: # status code is NOT 200, we have not succesfully gained access
            print("Error fetching data, Status Code 200")

    def name_to_cik(self, name): # returns cik from name
        return self.namedict.get(name.lower())

    def ticker_to_cik(self, ticker): # returns cik from ticker
        return self.tickerdict.get(ticker.lower())
    
    def cik_to_ticker(self, cik):
        return self.cikdict.get(cik, (None, None, None))[1]
    
    def removeLeadingZeros(self, cik):
        for i in range(len(cik)): 
            # check for the first non-zero character 
            if cik[i] != '0': 
                # return the remaining string 
                res = cik[i::]; 
                return res; 

    def getFiscalQuarter(self, quarter): #returns the fiscal quarter according to months
        if quarter == "01" or quarter == "02" or quarter == "03":
            return 1
        elif quarter == "04" or quarter == "05" or quarter == "06":
            return 2
        elif quarter == "07" or quarter == "08" or quarter == "09":
            return 3
        else:
            return 4
        
    def get_company_info(self):
        return {
            'accessionNumbers': self.company_info.get('accessionNumber', {}),
            'filingDates': self.company_info.get('filingDate', {}),
            'primaryDocuments': self.company_info.get('primaryDocument', {}),
            'primaryDocumentDescriptions': self.company_info.get('primaryDocDescription', {})
        }
    
    def getAuth(self,cik):
        link = f'https://data.sec.gov/submissions/CIK{cik}.json'
        header = {'user-agent': 'MLT GS skelete@ucsc.edu'} #requested by the SEC website in order to gain authorization
        data = requests.get(link, headers=header) #gets the information from the json file, with our header as a parameter
        return data
    
    def annual_filing(self,cik,year):
        data = self.getAuth(cik)

        if data.status_code == 200:
            self.company_info = data.json().get('filings', {}).get('recent',{})
            company_info = self.get_company_info()

            ticker = self.cik_to_ticker(cik).lower()
            index = 0
            cikShort = 0
            accNum = 0
            finDoc = ""
            
            for docDescription in company_info['primaryDocumentDescriptions']:
                if docDescription.find("10-K") != -1 or docDescription.find("10-Q") != -1:
                        index = company_info['primaryDocumentDescriptions'].index(docDescription)
                        if company_info['filingDates'][index][0:4] == year:
                            finDoc = company_info['primaryDocuments'][index]
                            accNum = (company_info['accessionNumbers'][index]).replace("-", "")
                            cikShort = self.removeLeadingZeros(cik)
            
            if cikShort == 0 or accNum == 0 or finDoc == "":
                return f"Annual filing not found for company: {ticker.upper()}"
            else:
                return f"https://www.sec.gov/Archives/edgar/data/{cikShort}/{accNum}/{finDoc}"
        else:
            print(f"Error fetching data, Status Code {data.status_code}")

    def quarterly_filing(self, cik, year, quarter):
        data = self.getAuth(cik)
        
        if data.status_code == 200:
            self.company_info = data.json().get('filings', {}).get('recent',{})
            company_info = self.get_company_info()
            
            ticker = self.cik_to_ticker(cik).lower()
            index = 0
            cikShort = 0
            accNum = 0
            finDoc = ""
            
            for docDescription in company_info['primaryDocumentDescriptions']:
                if docDescription.find("10-Q") != -1:
                    index = company_info['primaryDocumentDescriptions'].index(docDescription)
                    if company_info['filingDates'][index][0:4] == year and self.getFiscalQuarter(company_info['filingDates'][index][5:7]) == quarter:
                        finDoc = company_info['primaryDocuments'][index]
                        accNum = (company_info['accessionNumbers'][index]).replace("-", "")
                        cikShort = self.removeLeadingZeros(cik)
            
            if cikShort == 0 or accNum == 0 or finDoc == "":
                return f"Quarterly filing not found for company: {ticker.upper()}"
            else:
                return f"https://www.sec.gov/Archives/edgar/data/{cikShort}/{accNum}/{finDoc}"
        else:
            print(f"Error fetching data, Status Code {data.status_code}")

se = SecEdgar('https://www.sec.gov/files/company_tickers.json')


print(se.name_to_cik('MICROSOFT CORP'))
print(se.ticker_to_cik('AAPL'))
print(se.cik_to_ticker('0001045810'))

print(se.annual_filing('0001045810','2024'))
print(se.quarterly_filing('0000320193','2024',2))
