#region imports
from AlgorithmImports import *
#endregion
from nltk.sentiment import SentimentIntensityAnalyzer #分析twitter入邊既twit既sentiment情緒

class MyAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2012, 11, 1)
        self.SetEndDate(2017, 1, 1)
        self.SetCash(100000)
        
        #分鐘圖, 因為twit可以幾時出都OK
        self.tsla = self.AddEquity("TSLA", Resolution.Minute).Symbol

        #MuskTweet, 第二個係符號, 姐係個名, 第三個係時間分段, Symbol之後有用
        self.musk = self.AddData(MuskTweet, "MUSKTWTS", Resolution.Minute).Symbol
        
        #每日放左佢
        self.Schedule.On(self.DateRules.EveryDay(self.tsla),
                 self.TimeRules.BeforeMarketClose(self.tsla, 15),      
                 self.ExitPositions)

    def OnData(self, data):

        #如果data入邊有資料, 個資料呢度係refer to musk咁就分析
        if self.musk in data:
            #拎左個分數先
            score = data[self.musk].Value

            #拎埋個內容
            content = data[self.musk].Tweet
            
            #大過0.5就多, 細過0.5就空.
            if score > 0.5:
                self.SetHoldings(self.tsla, 1)
            elif score < -0.5:
                self.SetHoldings(self.tsla, -1)
                
                #絶對值
            if abs(score) > 0.5:
                self.Log("Score: " + str(score) + ", Tweet: " + content)


    #呢個功能係用黎放晒D股票
    def ExitPositions(self):
        self.Liquidate()

#PythonData Class Extention
class MuskTweet(PythonData):

    #情緒分析器既object.

    sia = SentimentIntensityAnalyzer()

    #呢個class唔再係QC ALGO CLASS, 所以用唔到佢入邊既功能function

    def GetSource(self, config, date, isLive):

        #dl = 1 dropbox文件一定要用, 如果dl = 0, 就會開你個website online
        source = "https://www.dropbox.com/s/ovnsrgg1fou1y0r/MuskTweetsPreProcessed.csv?dl=1"

        # 回傳返一個S_DataSource Obj , 個source係上邊個source
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile);

    def Reader(self, config, line, date, isLive):
        #如果無資料就唔做
        if not (line.strip() and line[0].isdigit()):
            return None
        #到分返一行行
        data = line.split(',')
        # Tweet會記錄呢個tweet
        tweet = MuskTweet()
        
        try:
            #呢個照打
            tweet.Symbol = config.Symbol

            #呢個係記錄時間
            tweet.Time = datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)

            #拎埋個內容, 英文黎
            content = data[1].lower()
            
            #搵有呢D字眼既tweet
            if "tsla" in content or "tesla" in content:
                #用呢個lib黎搵返個情緒值 拎返個compound值, 正數係開心, 負數係唔開心
                tweet.Value = self.sia.polarity_scores(content)["compound"]
            else:
                #如果無人講tsla, 就當無野
                tweet.Value = 0
            #"TWEET" 係所有內容, 記住晒佢
            tweet["Tweet"] = str(content)
            
            #如果有咩問題就咩咩咩啦
        except ValueError:
            return None
        #比返個tweet obj出去
        return tweet