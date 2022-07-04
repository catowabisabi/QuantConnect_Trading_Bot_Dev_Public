from AlphaModel import *

class VerticalTachyonRegulators(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)

        # Universe selection 
        # 選擇股票
        # 用於計算重組股票組合之時間間隔
        self.month = 0
        # 粗略的建議一些股票, 這個數是我們希望選手的股票的數量
        self.num_coarse = 500

        # 日線
        self.UniverseSettings.Resolution = Resolution.Daily
        # 加入股票去我們的股票池的方法有兩個, 粗略選擇, 和細仔選擇, 先運行粗選再運行細選
        self.AddUniverse(self.CoarseSelectionFunction, self.FineSelectionFunction)
        
        # Alpha Model Alpha股票建議模型, 這個Alpha在最開始導入。
        self.AddAlpha(FundamentalFactorAlphaModel())

        # Portfolio construction model
        # 這裏用的是每一個sector都投資一樣的價錢
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel(self.IsRebalanceDue))
        
        # Risk model
        # 這個Risk model什麼都不做, 我們都可以用QC 本身有的risk model
        self.SetRiskManagement(NullRiskManagementModel())

        # Execution model
        # 這個execution model是在股票組合決定後馬上買賣
        self.SetExecution(ImmediateExecutionModel())

    # Share the same rebalance function for Universe and PCM for clarity
    # 這個是用於決定重組股票組合分佈的時間, 分別是1月4月7月10月
    def IsRebalanceDue(self, time):
        # Rebalance on the first day of the Quarter
        if time.month == self.month or time.month not in [1, 4, 7, 10]:
            return None
            
        self.month = time.month
        return time

    # 粗選功能
    def CoarseSelectionFunction(self, coarse):
        # If not time to rebalance, keep the same universe
        # 如果不是1 4 7 10 月, 我們的股票組合不變
        if not self.IsRebalanceDue(self.Time): 
            return Universe.Unchanged

        # Select only those with fundamental data and a sufficiently large price
        # Sort by top dollar volume: most liquid to least liquid
        # 只選有fundamental data的股票, 這些股票的價錢需要至少有5蚊,  
        selected = sorted([x for x in coarse if x.HasFundamentalData and x.Price > 5],
                            # 另外用交易量排, 由最多排到最少
                            key = lambda x: x.DollarVolume, reverse=True)

        # 選好晒既股票係呢度
        return [x.Symbol for x in selected[:self.num_coarse]]

    # 細選功能
    def FineSelectionFunction(self, fine):
        # Filter the fine data for equities that IPO'd more than 5 years ago in selected sectors
        # 用morning star 入邊既 sector去分開唔同既股票, 先做一個list
        sectors = [
            MorningstarSectorCode.FinancialServices,
            MorningstarSectorCode.RealEstate,
            MorningstarSectorCode.Healthcare,
            MorningstarSectorCode.Utilities,
            MorningstarSectorCode.Technology]

        #只選擇IPO多過年和在這些sectors裏的股票        
        filtered_fine = [x.Symbol for x in fine if x.SecurityReference.IPODate + timedelta(365*5) < self.Time
                                    and x.AssetClassification.MorningstarSectorCode in sectors
                                    # 淨值報酬率 為正數
                                    and x.OperationRatios.ROE.Value > 0
                                    # 營業利益率 為正數
                                    and x.OperationRatios.NetMargin.Value > 0
                                    # 市盈率 為正數
                                    and x.ValuationRatios.PERatio > 0]
                
        return filtered_fine