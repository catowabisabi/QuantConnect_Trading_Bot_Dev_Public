from keras.utils.generic_utils import serialize_keras_object
from tensorflow.keras import utils
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
import json



# 設定機器學習所使用資料的年期 - 可以修改
start = datetime(2017, 1, 1)
end = datetime(2022, 1, 1)




# QuantBook 可以使用所有的QC research API
qb = QuantBook()
# 設定要練習的資料的symbol, 在這是合是BTCUSD每日的線
symbol = qb.AddCrypto("BTCUSD", Resolution.Daily).Symbol
# symbol = qb.AddEquity("SPY", Resolution.Daily).Symbol
# 會之前兩年的資料, 拿symbol的那一行的資料
history = qb.History(symbol, start, end).loc[symbol]
history.head()



# 拿每一日的開收巿價, 最高最底價和成交量變化的百份比
daily_pct_change = history[["open", "high", "low", "close", "volume"]].pct_change().dropna()
df = daily_pct_change
df.head()



# 呢句我唔太明, 但佢既意思係係df入邊, 如果佢volume係無限大, 拎佢既index出黎
# 然後這些index 做一個drop indexes動作

indexes = df[((df.volume == float("inf")))].index
for i in indexes:
    df.at[i, "volume"] = max(df.volume.drop(indexes))
    


#要放D DATA 入去神經網絡, 要有特定資料format

# 要入前30日的資料, 所以呢30日唔要
n_steps = 30
features = [] # 入的資料
labels = [] # 想佢出的資料


# 由最新既資料到最後既資料, 唔要最尾尾個30日
for i in range(len(df)-n_steps):

        
    input_data = df.iloc[i:i+n_steps].values
    features.append(input_data)
    if df['close'].iloc[i+n_steps] >= 0:
        # UP # 升價
        label = 1
    else:
        # DOWN 降價
        label = 0
    labels.append(label)



# 變為numpy array, 因為呢個係Tensorflow需要用既格式
features = np.array(features)
labels = np.array(labels)



#用 7成既資料去做Training data
#之後3成就做testing 

train_length = int(len(features) * 0.7)
X_train = features[:train_length]
X_test = features[train_length:]
y_train = labels[:train_length]
y_test = labels[train_length:]




# number of up vs down days in training data should be relatively balanced
# check下本身有幾多日係升
sum(y_train)/len(y_train)




# use second part of data for training instead
# 用後邊個一半去做training
test_length = int(len(features) * 0.3)
X_train = features[test_length:]
X_test = features[:test_length]
y_train = labels[test_length:]
y_test = labels[:test_length]




# check下本身有幾多日係升
sum(y_train)/len(y_train)




# Keras
model = Sequential([Dense(30, input_shape=X_train[0].shape, activation='relu'),
                    Dense(20, activation='relu'),
                    Flatten(),
                    Dense(1, activation='sigmoid')])




model.compile(loss='binary_crossentropy',
                optimizer='adam',
                metrics=['accuracy', 'mse'])



model.fit(X_train, y_train, epochs=50)




# 試下得唔得,
y_hat = model.predict(X_test)




#出返個results
results = pd.DataFrame({'y': y_test.flatten(), 'y_hat': y_hat.flatten()})




# 畫圖
results.plot(title='Model Performance: predicted vs actual %change in closing price', figsize=(30, 7))




# 寫出這個學習的結果
pred_train= model.predict(X_train)
scores = model.evaluate(X_train, y_train, verbose=0)
print('Accuracy on training data: {}% \n Error on training data: {}'.format(scores[1], 1 - scores[1]))

# 寫出這個測試的結果
pred_test= model.predict(X_test)
scores2 = model.evaluate(X_test, y_test, verbose=0)
print('Accuracy on test data: {}% \n Error on test data: {}'.format(scores2[1], 1 - scores2[1]))






#SAVE MODEL
# 存左個模型入去model str
model_str = json.dumps(serialize_keras_object(model))



# 比一個model key個model
model_key = 'bitcoin_price_predictor'




# save左佢
qb.ObjectStore.Save(model_key, model_str)





#LOAD MODEL

# 如果qb store入邊有model_key, 就拎佢出黎用
if qb.ObjectStore.ContainsKey(model_key):
    model_str = qb.ObjectStore.Read(model_key)
    #變成json
    config = json.loads(model_str)['config']
    #再變成要用既class
    model = Sequential.from_config(config)



# 用黎做測試的Date係用宜家
testDate = datetime.now()




# 拎最近40日既資料
df = qb.History(symbol, testDate - timedelta(40), testDate).loc[symbol]
df_change = df[["open", "high", "low", "close", "volume"]].pct_change().dropna()

#變成要用既format
model_input = []

for index, row in df_change.tail(30).iterrows():
    model_input.append(np.array(row))
model_input = np.array([model_input])



if round(model.predict(model_input)[0][0]) == 0:
    print("down")
else:
    print("up")