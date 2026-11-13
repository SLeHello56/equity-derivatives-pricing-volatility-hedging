"""Optional real market context: FRED SP500 levels and VIXCLS volatility index.
Historical spot and VIX are NOT an option chain or matched implied-vol smile.
"""
from io import StringIO
import pandas as pd
import requests

ALLOWED={'SP500','VIXCLS'}
def fetch_fred(series,start='2022-01-01',end=None):
    if series not in ALLOWED: raise ValueError(f'Allowed FRED series: {sorted(ALLOWED)}')
    params={'id':series,'cosd':start}
    if end: params['coed']=end
    r=requests.get('https://fred.stlouisfed.org/graph/fredgraph.csv',params=params,timeout=30)
    r.raise_for_status()
    df=pd.read_csv(StringIO(r.text))
    col='observation_date' if 'observation_date' in df else 'DATE'
    df=df.rename(columns={col:'date',series:'value'})
    if not {'date','value'}.issubset(df): raise ValueError('Unexpected FRED response')
    df['date']=pd.to_datetime(df.date)
    df['value']=pd.to_numeric(df.value,errors='coerce')
    return df.dropna().reset_index(drop=True)
