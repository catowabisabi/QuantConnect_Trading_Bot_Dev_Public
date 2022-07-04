class FundamentalFactorAlphaModel(AlphaModel):
    
    #python 最根本的init
    #
    def __init__(self):
        self.rebalanceTime = datetime.min
        # Dictionary containing set of securities in each sector
        # e.g. {technology: set(AAPL, TSLA, ...), healthcare: set(XYZ, ABC, ...), ... }
        #這個model會儲存我所定立的sector, 這個sectors資料會由main拎入黎
        self.sectors = {}

    def Update(self, algorithm, data):
        '''Updates this alpha model with the latest data from the algorithm.
        This is called each time the algorithm receives data for subscribed securities
        Args:
            algorithm: The algorithm instance
            data: The new data available
        Returns:
            New insights'''
            # 這裏的empty list 是沒有insight的意思, 
        if algorithm.Time <= self.rebalanceTime:
            return []
        
        # Set the rebalance time to match the insight expiry
         # 個日期改過每季最後一日, 有個時間係度。
        self.rebalanceTime = Expiry.EndOfQuarter(algorithm.Time)
        
        insights = []
        
        for sector in self.sectors:
            #在每個行業中的所有股票中, 排列
            securities = self.sectors[sector]
            sortedByROE = sorted(securities, key=lambda x: x.Fundamentals.OperationRatios.ROE.Value, reverse=True)
            sortedByPM = sorted(securities, key=lambda x: x.Fundamentals.OperationRatios.NetMargin.Value, reverse=True)
            sortedByPE = sorted(securities, key=lambda x: x.Fundamentals.ValuationRatios.PERatio, reverse=False)

            # Dictionary holding a dictionary of scores for each security in the sector
            scores = {}
            # 在每一個股業中, 把每一排行量化, 然後...加起來, 行出一個分數
            for security in securities:
                score = sum([sortedByROE.index(security), sortedByPM.index(security), sortedByPE.index(security)])
                scores[security] = score
                
            # Add best 20% of each sector to longs set (minimum 1)
            #要買的股票數的計算 = 我們池中有的股的數量 除5 , 如果比少, 就用1 (INT會四/5入, 所以至少係0, 但如果係0會變1)
            length = max(int(len(scores)/5), 1)

            # 呢度既分數係代表一個股票, 佢宜家要排咁多, 分高排前邊, 之後就係選擇上邊計左既20%既數目
            for security in sorted(scores.items(), key=lambda x: x[1], reverse=False)[:length]:
                symbol = security[0].Symbol
                # Use Expiry.EndOfQuarter in this case to match Universe, Alpha and PCM
                insights.append(Insight.Price(symbol, Expiry.EndOfQuarter, InsightDirection.Up))
        
        return insights

    def OnSecuritiesChanged(self, algorithm, changes):
        '''Event fired each time the we add/remove securities from the data feed
        Args:
            algorithm: The algorithm instance that experienced the change in securities
            changes: The security additions and removals from the algorithm'''
        
        # Remove security from sector set
        # 當發生Securities Changed, 在 移除的股票中 的股票中
        for security in changes.RemovedSecurities:
            # 在self 行業中的每一個行業中
            for sector in self.sectors:
                # 如果 這個行業分類中有 這支  在移除的股票中 的股票
                if security in self.sectors[sector]:
                    # 把這股票移除
                    self.sectors[sector].remove(security)
        
        # Add security to corresponding sector set
        for security in changes.AddedSecurities:
            #
            sector = security.Fundamentals.AssetClassification.MorningstarSectorCode

            # 如果這個行業不在我們現有的行業清單中
            if sector not in self.sectors:
                # 這個行業(Morning Star 中記綠的我們所選的行業清單) 變為 個新的SET
                self.sectors[sector] = set()
                #我們在這個SET中加入我們選的行業
            self.sectors[sector].add(security)