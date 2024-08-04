import requests

#retrieves data from the U.S. Securities and Exchange Commission (SEC) and returns a company's CIK
class SecEdgar:
    #initializes all variables needed for retrieving information
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.cikdict = {}
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
                cik = str(info['cik_str']).zfill(10)
                ticker = info['ticker']
                name = info['title']

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
    
    def cik_to_ticker(self, cik): # returns ticker from cik
        return self.cikdict.get(cik, (None, None, None))[1]
    
    def removeLeadingZeros(self, cik): #removes leading zeros for cik
        return cik.lstrip('0') 

    def getFiscalQuarter(self, quarter): #returns the fiscal quarter according to months
        if quarter == "01" or quarter == "02" or quarter == "03":
            return 1
        elif quarter == "04" or quarter == "05" or quarter == "06":
            return 2
        elif quarter == "07" or quarter == "08" or quarter == "09":
            return 3
        else:
            return 4
        
    def get_company_info(self): # function that gets all required company information from the json file
        return {
            'accessionNumbers': self.company_info.get('accessionNumber', {}),
            'filingDates': self.company_info.get('filingDate', {}),
            'primaryDocuments': self.company_info.get('primaryDocument', {}),
            'primaryDocumentDescriptions': self.company_info.get('primaryDocDescription', {})
        }
    
    def getAuth(self,cik): # function that sends authorization and receives data from sec website
        link = f'https://data.sec.gov/submissions/CIK{cik}.json' #link to the specific cik json file storing all important data
        header = {'user-agent': 'MLT GS skelete@ucsc.edu'} #requested by the SEC website in order to gain authorization
        data = requests.get(link, headers=header) #gets the information from the json file, with our header as a parameter
        return data
    
    def get_filing_link(self, cik, year, doc_type, quarter=None):
        data = self.getAuth(cik)  # send authorization and receive data

        if data.status_code == 200:  # if data is received successfully
            self.company_info = data.json().get('filings', {}).get('recent', {})  # get company's recent filing information
            company_info = self.get_company_info()  # get all necessary arrays that store crucial information

            # local variables used to store desired document information
            ticker = self.cik_to_ticker(cik).lower()  # get the ticker name
            cikShort = self.removeLeadingZeros(cik)  # remove the leading zeros to be used in the link

            for index, docDescription in enumerate(company_info['primaryDocumentDescriptions']):  # cycle through all primary document descriptions
                if docDescription.find(doc_type) != -1:  # if the current document is the desired type
                    if company_info['filingDates'][index][0:4] == year and (quarter is None or self.getFiscalQuarter(company_info['filingDates'][index][5:7]) == quarter):
                        finDoc = company_info['primaryDocuments'][index]  # get the desired primary doc
                        accNum = company_info['accessionNumbers'][index].replace("-", "")  # remove the dash marks from the accession number
                        return f"https://www.sec.gov/Archives/edgar/data/{cikShort}/{accNum}/{finDoc}"  # return link

            return f"{doc_type} filing not found for company: {ticker.upper()}"  # return error if not found
        else:
            print(f"Error fetching data, Status Code {data.status_code}")  # if not status code 200, return error

    def annual_filing(self, cik, year):
        return self.get_filing_link(cik, year, "10-K")

    def quarterly_filing(self, cik, year, quarter):
        return self.get_filing_link(cik, year, "10-Q", quarter)


se = SecEdgar('https://www.sec.gov/files/company_tickers.json')


print(se.name_to_cik('MICROSOFT CORP'))
print(se.ticker_to_cik('AAPL'))
print(se.cik_to_ticker('0001045810'))

print(se.annual_filing('0001045810','2022'))
print(se.quarterly_filing('0000320193','2023',2))
