#!/usr/bin/env python
# coding: utf-8

# In[1]:


import coinmarketcapapi as cmc
import pandas as pd
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager


# In[2]:


import warnings
warnings.filterwarnings("ignore")


# In[3]:


def crypto_data(api):
    global pd
    global usd_Price
    global ind_crypto_df
    global currencies
    global cmc_df
    
    user = cmc.CoinMarketCapAPI(api)
    price = user.cryptocurrency_listings_latest()
    cmc_df = pd.DataFrame(price.data)
    id_map = user.cryptocurrency_map()
    pd_1 = pd.DataFrame(id_map.data, columns =['name','symbol'])
    currencies = pd.DataFrame(pd_1['symbol'])
    currencies['Length'] = currencies['symbol'].str.len()
    cmc_df = cmc_df[cmc_df['last_updated'].notnull()]
    
    ind_crypto_df = cmc_df[['symbol', 'last_updated', 'quote']]
    ind_crypto_dict = dict(ind_crypto_df['quote'])
    usd_Price = []
    
    for i in ind_crypto_dict:
        usd_Price.append(ind_crypto_dict.get(i).get('USD').get('price'))
        
    ind_crypto_df['USD_Price']=usd_Price
    ind_crypto_df = ind_crypto_df.drop('quote', axis = 1)
    return currencies


# In[4]:


def asset(api_key, api_secret):
    global asset_of_choice
    global price_df
    global asset_amount
    global split
    global base
    global rev_df
    global price_final
    global user
    
    user = Client(api_key, api_secret)
    price = user.get_all_tickers()
    price_df = pd.DataFrame(price)
    
    user_account = user.get_account()
    user_account_df = pd.DataFrame(user_account['balances'])
    user_account_df = user_account_df.astype({'free':'float', 'locked':'float'})
    user_account_df['Total'] = user_account_df['free'] + user_account_df['locked']
    wallet_with_charge = user_account_df[user_account_df.Total == user_account_df.Total.max()]
    asset_of_choice = wallet_with_charge['asset']
    asset_amount = wallet_with_charge['Total']
    
    split = []
    
    for x in price_df['symbol']:
        for y in currencies['symbol']:
            if x[:5] == y or x[:4] == y or x[:3] == y:
                s_str = x[:len(y)]
                break
                
        split.append(s_str)

        
    price_df['Quote'] = split
    base = []
    
    for j in range(len(price_df['Quote'])):
        base.append(price_df['symbol'][j][len(price_df['Quote'][j]):])
    
    price_df['Base'] = base
    price_df['Rev_Symbol'] = price_df['Base'] + price_df['Quote']
    price_df = price_df.astype({'price':'float'})
    price_df['Rev_Price'] = 1/price_df['price']
    rev_df = price_df[['Rev_Symbol', 'Rev_Price']]
    price_df = price_df.drop(['Rev_Symbol', 'Rev_Price'], axis = 1)
    rev_df = rev_df.rename(columns = {'Rev_Symbol':'symbol', 'Rev_Price':'price'})
    price_final = pd.concat([price_df, rev_df])
    price_final = price_final.reset_index()
    price_final = price_final.drop(['Quote', 'Base'], axis = 1)
    price_final = price_final.drop_duplicates(['symbol'])
    return price_final


# In[5]:


crypto_data('dc692405-b633-4aa9-8273-20dcf1edef1f')


# In[6]:


asset("7aZQgcF9aH7QpAdfxMgT6QZvFfhK97mA9kErtBPZPPrbDjOlVxk8ctDfmLjcPJUC", "iXfFrrpvMa3z18XGFnrPKHgCZgR9gLwpSRh1URWDGP0joAw8Y5V6h0n9rX6RBFeo")


# In[7]:


price_final = price_final.drop('index', axis = 1)


# In[8]:


asset_amount = float(asset_amount)


# In[94]:


def profitability(amount, asset_n, asset_m):
    profit_list = []
    
    crypto_exchange = str(asset_m) + str(asset_n)
    if crypto_exchange in list(price_final['symbol']):
        index_crypto_exchange = list(price_final['symbol']).index(crypto_exchange)
                
        # Getting the price of asset_m and calculating its amount that can be purchased
        conversion_rate = price_final['price'].iloc[index_crypto_exchange]
        asset_m_amount = float(amount/conversion_rate)
                
        # Getting the value of 'n' and 'm' asset in terms of USD
        price_in_usd_m = list(project_df.loc[(project_df['symbol']==asset_m)]["USD_Price"])[0]
        price_in_usd_n = list(project_df.loc[(project_df['symbol']==asset_n)]["USD_Price"])[0]

        # Getting the fiat value of 'n' and 'm' assets
        fiat_m = asset_m_amount*price_in_usd_m
        fiat_n = amount*price_in_usd_n
        # Checking for possible profits
        if fiat_m > fiat_n:
            profit = fiat_m - fiat_n
            profit_list.append(profit)
            profit_singular=[asset_n, asset_m, crypto_exchange, profit]
            
        else:
            return
    
    else:
        return
    
    return profit_singular


# In[95]:


def algo_trade_3(amount):
    
    global symb 
    global project_df 
    profit_pth_arr = []
    project_df = ind_crypto_df    
    symb = project_df['symbol']
    
    
    # n ---> base_asset
    # m ---> quote asset
    
    asset_n = "LINK" # Initialise the asset_n variable
    count = 0
    while count <= len(symb):
        
        count = count+1
        
        # Getting the asset_m variable
        for index_m in enumerate(symb):
            index_value = index_m[0]
            asset_m = symb.iloc[index_value]
            profit_pth_single = profitability(asset_amount, asset_n, asset_m)
            
            if profit_pth_single:
                profit_pth_arr.append(profit_pth_single)

            
            
        # Creating a dataframe of all 'profit_path' and sorting it
            
        success_path = pd.DataFrame(profit_pth_arr, columns = ['Base_Asset', 'Quote_Asset','TradePair', 'Profit'])
        trade_path_df = success_path.sort_values('Profit', ascending = False).drop_duplicates(['Base_Asset'])
        
        # Creating a dataframe of the max value with respect to 'asset_n'
        single_row_df = trade_path_df.loc[trade_path_df['Base_Asset'] == asset_n]
        #print('hello_3')
        
        # Checking for the length of the dataframe 
        if len(single_row_df) == 0:
            continue
        
        else:

            #Updating the value of 'asset_n' by selecting from 'single_row_df'
            asset_n = single_row_df.iloc[0][1]
            #print(asset_n)
            # Creating the combination of strings
            updated_string_exchange = asset_n + str(single_row_df.iloc[0][0])
     

            # Checking for the existence of 'updated_string_exchange' in Binance data
            if updated_string_exchange in list(price_final['symbol']):
                if updated_string_exchange not in profit_pth_arr:
                    index_for_updation = list(price_final['symbol']).index(updated_string_exchange)
                    conversion_for_updation = price_final['price'].iloc[index_for_updation]
                
                    #Updating the 'amount' value
                    amount = float(amount/conversion_for_updation)
                    #print('hello_4')
                else:
                    break
         
            else:
                continue
            
                    


        
    return trade_path_df


# In[96]:


prof_df = algo_trade_3(asset_amount)


# In[97]:


prof_df


# In[ ]:




