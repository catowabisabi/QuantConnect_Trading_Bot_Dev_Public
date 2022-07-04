from collections import deque

class AdaptableSkyBlueHornet(QCAlgorithm):

    def Initialize(self):
        #呢度係用黎backtest
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

#一開始就緊係拎左D我地要既資料返黎先, 呢度係SMA
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        #拎每日既SPY BAR, 拎30日
    #    self.sma = self.SMA(self.spy, 30, Resolution.Daily)
        
        #
        # History warm up for shortcut helper SMA indicator

        #呢度拎每一日既收巿價
    #    closing_prices = self.History(self.spy, 30, Resolution.Daily)["close"]

        #呢兩行係update返SMA入邊既數, 等佢可以出返個30日既SMA出黎
    #    for time, price in closing_prices.loc[self.spy].items():
    #        self.sma.Update(time, price)
        
        # Custom SMA indicator

        self.sma = CustomSimpleMovingAverage("CustomSMA", 30)

        # 修改返個SMA既definition, 要入三樣野, 第一個係呢個SMA係邊個股票既, 
        # 第三個係呢個indicator係乜, 呢度係SMA, 第三個係佢要頂左邊個SMA既時間值, 
        # 呢度係頂左daily
        self.RegisterIndicator(self.spy, self.sma, Resolution.Daily)

    
    def OnData(self, data):

        #未拎到SMA之前唔好行住, 再做一次
        if not self.sma.IsReady:
            return
        
        # Save high, low, and current price 呢度拎之前365日既資料, 拎最高最低價
        hist = self.History(self.spy, timedelta(365), Resolution.Daily)
        low = min(hist["low"])
        high = max(hist["high"])
        

        #呢呢隻股票最新價
        price = self.Securities[self.spy].Price
        
        #如果價錢突破365日既最高價, 同埋, 宜家既價錢都高過最近30日既最高價, 咁姐係...個巿做好, 就買升
        # Go long if near high and uptrending
        if price * 1.05 >= high and self.sma.Current.Value < price:
            #當然要睇埋我地本身有無買, 如果無就all in
            if not self.Portfolio[self.spy].IsLong:
                self.SetHoldings(self.spy, 1)
        
        # Go short if near low and downtrending
        elif price * 0.95 <= low and self.sma.Current.Value > price:  
            if not self.Portfolio[self.spy].IsShort:
                #呢句係話如果無short緊, 我地就short晒所有
                self.SetHoldings(self.spy, -1)
        
        # Otherwise, go flat
        else:
            self.Liquidate()
        

        self.Plot("Benchmark", "52w-High", high)
        self.Plot("Benchmark", "52w-Low", low)
        self.Plot("Benchmark", "SMA", self.sma.Current.Value)


class CustomSimpleMovingAverage(PythonIndicator):
    
    def __init__(self, name, period): #一開始要入邊要拎幾多個數比佢先
        self.Name = name
        self.Time = datetime.min
        self.Value = 0

        #一開始要set返個平均數係幾多, 呢個數字係上邊有有
        self.queue = deque(maxlen=period)

    def Update(self, input):
        #右邊入一個數, 左邊拎走一個數
        self.queue.appendleft(input.Close)

        #
        self.Time = input.EndTime

        #所有數既有幾多數
        count = len(self.queue)

        #每一個queue加埋晒再除返咁多個
        self.Value = sum(self.queue) / count

        # returns true if ready
        #一開始未有數之前呢, 就唔好return住, 要等有晒咁多個數先. 個數係一開始set左
        return (count == self.queue.maxlen)