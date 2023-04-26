import json
import pandas as pd
import requests
from flask import Flask, request, Response

#constants
token = '6243489326:AAFSHqcB1eXqqkCFyBQa1i0rEzqkw5SjJVU'


#making requests - info about the bot

# https://api.telegram.org/bot6243489326:AAFSHqcB1eXqqkCFyBQa1i0rEzqkw5SjJVU/getMe

# #get updates - pegando a mesangem enviada ao telegram
# https://api.telegram.org/bot6243489326:AAFSHqcB1eXqqkCFyBQa1i0rEzqkw5SjJVU/getUpdates

# #get updates - pegando a mesangem enviada ao telegram
# https://api.telegram.org/bot6243489326:AAFSHqcB1eXqqkCFyBQa1i0rEzqkw5SjJVU/setWebhook?url=https://localhost.run/docs/forever-free/


# #send message - bot envia a mensagem
# https://api.telegram.org/bot6243489326:AAFSHqcB1eXqqkCFyBQa1i0rEzqkw5SjJVU/sendMessage?chat_id=1683057015&text=Hi Alexandre, to de boa!

def send_message(chat_id, text):
    url = 'https://api.telegram.org/bot{}/'.format(token)
    url = url + 'sendMessage?chat_id={}'.format(chat_id)
    
    #passando o texto
    r= requests.post(url, json={'text': text})

    print('status code {}'.format(r.status_code))

    return None
    


def load_dataset(store_id):

    df10 = pd.read_csv('/home/alexandrerod/Documentos/repos/DataScienceProd/Data/test.csv')
    df_store_raw = pd.read_csv('/home/alexandrerod/Documentos/repos/DataScienceProd/Data/store.csv', low_memory=False)
    
    
    # merge test dataset + store
    df_test = pd.merge( df10, df_store_raw, how='left', on='Store' )
    # choose store for prediction
    df_test = df_test[df_test['Store'] == store_id]

    if not df_test.empty:
        # remove closed days
        df_test = df_test[df_test['Open'] != 0]
        df_test = df_test[~df_test['Open'].isnull()]
        df_test = df_test.drop( 'Id', axis=1 )
        data = json.dumps( df_test.to_dict( orient='records' ) )
    else:
        data='error'

    return data

# convert Dataframe to json


# API Call
# url = 'http://127.0.0.1:5000/rossmann/predict'
def predict_data(data):
    url = 'https://rosmann-api-h9k2.onrender.com/rossmann/predict'
    header = {'Content-type': 'application/json' }
    data = data
    r = requests.post( url, data=data, headers=header )
    print( 'Status Code {}'.format( r.status_code ) )
    
    
    d1 = pd.DataFrame( r.json(), columns=r.json()[0].keys() )
    return d1

# API initialize
app = Flask(__name__)

#endpoint

@app.route('/', methods=['GET', 'POST'])

def parse_message(message):

    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']

    store_id = store_id.replace('/', '')

    try:
        store_id = int(store_id)
    
    except ValueError:
        store_id = 'error'

    
    return chat_id, store_id

def index():
    if request.method == 'POST':
        message= request.get_json()

        chat_id, store_id = parse_message(message)
        if store_id != 'error':
            #loading data
            if data != 'error':
                data = load_dataset(store_id)
                #prediction
                d1 = predict_data(data)
                #calculation
                d2 = d1[['store', 'prediction']].groupby( 'store' ).sum().reset_index()           
                #send message
                msg = 'Store Number {} will sell R${:,.2f} in the next 6 weeks'.format(
                d2['store'].values[0],
                d2['prediction'].values[0] ) 

                send_message(chat_id, msg)
                return Response('Ok', status=200)

            else:
                send_message(chat_id, 'Store Not Available')
                return Response('Ok', status=200)                 

        else:
            send_message(chat_id, 'Store ID is Wrong')
            return Response('Ok', status=200)

    else:

        return '<h1> Rossmann Telegram BOT </h1>'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)













# d2 = d1[['store', 'prediction']].groupby( 'store' ).sum().reset_index()
# for i in range( len( d2 ) ):
    # print( 'Store Number {} will sell R${:,.2f} in the next 6 weeks'.format(
        # d2.loc[i, 'store'],
        # d2.loc[i, 'prediction'] ) )