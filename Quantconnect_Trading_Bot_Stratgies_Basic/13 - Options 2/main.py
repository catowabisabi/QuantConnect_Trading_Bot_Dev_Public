#region imports
from AlgorithmImports import *
#endregion
# Watch my Tutorial: https://youtu.be/Lq-Ri7YU5fU

from datetime import timedelta 
from QuantConnect.Data.Custom.CBOE import * #CBOE數據可以提供 波動指數的價格與相關數據, 與VIX, VIX 提供標普500的隱含波動
#用這些數值去計算相對於歷史中的相對波動

#Exercise Price, Strike Price，或稱行使價、執行價格


class OptionChainProviderPutProtection(QCAlgorithm):

    def Initialize(self):
        # set start/end date for backtest 回測時間
        self.SetStartDate(2017, 10, 1)
        self.SetEndDate(2020, 10, 1)

        # set starting balance for backtest
        self.SetCash(100000)

        # SPY 一分線
        # add the underlying asset
        self.equity = self.AddEquity("SPY", Resolution.Minute)

        #期權只支持原始定價數據, 在回測中, 我們的投入不會影響股票分割或價格
        self.equity.SetDataNormalizationMode(DataNormalizationMode.Raw)
        self.symbol = self.equity.Symbol


        # add VIX data #拎左VIX先
        self.vix = self.AddData(CBOE, "VIX").Symbol


        # initialize IV indicator 波動先定為零 indicator of volatility
        self.rank = 0

        #
        # initialize the option contract with empty string
        self.contract = str()

        #可以keep住知道我地個set入邊有咩options既資料, 如果有就唔使再入
        self.contractsAdded = set()
        
        # parameters ------------------------------------------------------------
        #呢D係可以修改既參數

        
        self.DaysBeforeExp = 2 # number of days before expiry to exit 仲有幾多日打把
        self.DTE = 25 # target days till expiration 想搵幾多日內打把既期權證
        self.OTM = 0.01 # target percentage OTM of put  每一次只係比1%做保證金
        self.lookbackIV = 150 # lookback length of IV indicator 宜家既數據對比返之前既150日
        self.IVlvl = 0.5 # enter position at this lvl of IV indicator 如果波動值高過0.5, 就買保護性期權去保住自己既本金
        self.percentage = 0.9 # percentage of portfolio for underlying asset #9成會去買SPY
        self.options_alloc = 90 # 1 option for X num of shares (balanced would be 100) #我地每90股SPY就買1手options去保護
        # ------------------------------------------------------------------------
    
        # schedule Plotting function 30 minutes after every market open

        self.Schedule.On(self.DateRules.EveryDay(self.symbol), \
                        #每日
                        self.TimeRules.AfterMarketOpen(self.symbol, 30), \
                        #每日開巿後30分鐘
                        self.Plotting)
                        #繪圖


        # schedule VIXRank function 30 minutes after every market open
        self.Schedule.On(self.DateRules.EveryDay(self.symbol), \
                        self.TimeRules.AfterMarketOpen(self.symbol, 30), \
                        self.VIXRank)
                        #拎VIX值


        # warmup for IV indicator of data
        self.SetWarmUp(timedelta(self.lookbackIV)) 
        #

    #
    def VIXRank(self):
        #拎歷史, 用既係CBOE, 入去self vix, 睇返150日, 每日睇
        history = self.History(CBOE, self.vix, self.lookbackIV, Resolution.Daily)
        # (Current - Min) / (Max - Min)
        #現時的VIX, 等於(現時VIX PRICE - 歷史低位 )/ 歷史價差

        # 0 - 1
        # 數為1, 姐係宜家係new HIGH, 其實會大過, 不過一到一就姐係同之前一樣
        self.rank = ((self.Securities[self.vix].Price - min(history["low"])) / (max(history["high"]) - min(history["low"])))
 
    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''

        #有資料未
        if(self.IsWarmingUp):
            return
        
        # buy underlying asset 用上邊SET既90去買9成PSY
        if not self.Portfolio[self.symbol].Invested:
            self.SetHoldings(self.symbol, self.percentage)
        
        # buy put if VIX relatively high 如果IV 大過0.5 姐係好快到高點, 係呢度買個put option可以頂住先, 
        if self.rank > self.IVlvl:
            self.BuyPut(data)
        
        # close put before it expires
        #手度如果有contract係手, 就..
        if self.contract:
            # 如果張contract就到期,就賣左佢
            if (self.contract.ID.Date - self.Time) <= timedelta(self.DaysBeforeExp):
                self.Liquidate(self.contract)
                self.Log("Closed: too close to expiration")
                self.contract = str()

    def BuyPut(self, data):

        # get option data
        #如果無野, 就開optionsfilter搵上邊要既野 (要買咩options)
        if self.contract == str():
            self.contract = self.OptionsFilter(data)
            return
        
        #如果無投資緊, 而data入邊有有 我地想買既option既key, 姐係資料, 我地就買, 買返上邊定既比例
        # if not invested and option data added successfully, buy option
        elif not self.Portfolio[self.contract].Invested and data.ContainsKey(self.contract):
            self.Buy(self.contract, round(self.Portfolio[self.symbol].Quantity / self.options_alloc))

    def OptionsFilter(self, data):
        ''' OptionChainProvider gets a list of option contracts for an underlying symbol at requested date.
            Then you can manually filter the contract list returned by GetOptionContractList.
            The manual filtering will be limited to the information included in the Symbol
            (strike, expiration, type, style) and/or prices from a History call '''

        #拎晒成個表既所有options 出黎 只係SPY options
        contracts = self.OptionChainProvider.GetOptionContractList(self.symbol, data.Time)

        #SET呢D野 , 我地之前SET既價錢, +-2
        self.underlyingPrice = self.Securities[self.symbol].Price
        # filter the out-of-money put options from the contract list which expire close to self.DTE num of days from now
        #成張LIST每一個權拎出黎, 如果佢係put, 同1佢 係可接受既underlining price入邊, , 個差

        otm_puts = [i for i in contracts if i.ID.OptionRight == OptionRight.Put and
                                            #要買夠咁多既期權, 呢度既OTM 係上邊SET左做1% 
                                            self.underlyingPrice - i.ID.StrikePrice > self.OTM * self.underlyingPrice and
                                            # 想買既Experation Date +- 8 日, 呢度options既時間, 姐係一星期前後都OK, 呢度既DTE係25日, 姐係做17日至33日既options 先買
                                            self.DTE - 8 < (i.ID.Date - data.Time).days < self.DTE + 8]

        if len(otm_puts) > 0:
            # sort options by closest to self.DTE days from now and desired strike, and pick first
            # 先排左個strike price先, 拎最平個個, 之後再排最接近25日個個
            contract = sorted(sorted(otm_puts, key = lambda x: abs((x.ID.Date - self.Time).days - self.DTE)),
                                                     key = lambda x: self.underlyingPrice - x.ID.StrikePrice)[0]
                
                #如果呢張合約唔係我地個list度,咁就加入我地個list度, 咁可以防止我地買完又買同一張
            if contract not in self.contractsAdded:
                self.contractsAdded.add(contract)

                # use AddOptionContract() to subscribe the data for specified contract
                self.AddOptionContract(contract, Resolution.Minute)

            return contract

        else:
            return str()

    def Plotting(self):

        # plot IV indicator 繪圖: IV 
        self.Plot("Vol Chart", "Rank", self.rank)

        # plot indicator entry level 繪圖: Entry Level
        self.Plot("Vol Chart", "lvl", self.IVlvl)

        # plot underlying's price 繪圖, 相關資產(Underlying Asset)
        self.Plot("Data Chart", self.symbol, self.Securities[self.symbol].Close)

        # plot strike of put option 繪圖: Strike Price 行使價
        option_invested = [x.Key for x in self.Portfolio if x.Value.Invested and x.Value.Type==SecurityType.Option]
        if option_invested:
                self.Plot("Data Chart", "strike", option_invested[0].ID.StrikePrice)

    def OnOrderEvent(self, orderEvent):
        # 記低自己做過既買賣
        # log order events
        self.Log(str(orderEvent))