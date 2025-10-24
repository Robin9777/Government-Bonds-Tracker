import pandas as pd
import requests
import os

class EodhdAPIClient:

    API_TOKEN = " 68f9e0d9e102d1.33785257"
    BASE_URL = "https://eodhd.com/api/eod/"

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or self.BASE_URL

    def _get(self, endpoint: str):
        url = f"{self.base_url}/{endpoint}"
        data = requests.get(url).json()

        return pd.DataFrame(data)
    
class GovBondRequest:

    def __init__(self, debt: str="DE", maturity: str="10Y", client: EodhdAPIClient | None = None):

        self.debt = debt
        self.maturity = maturity
        self.client = client or EodhdAPIClient()

    def get_eod(self):

        endpoint = f"{self.debt}{self.maturity}.GBOND?api_token={self.client.API_TOKEN}&fmt=json&"
        data = self.client._get(endpoint)
        
        return data
    
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

debts = ["FR"] # to modify
maturities = ["2Y", "5Y", "10Y", "30Y"] # 

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

for i, d in enumerate(debts):
    for j, m in enumerate(maturities):
        data = GovBondRequest(d, m).get_eod()
        file_path = os.path.join("GovDatas", f"{d}_{m}.parquet")
        data.to_parquet(file_path)