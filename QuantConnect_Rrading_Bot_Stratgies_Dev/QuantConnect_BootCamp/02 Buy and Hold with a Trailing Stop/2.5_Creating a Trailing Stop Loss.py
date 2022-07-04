class BootCampTask(QCAlgorithm):
    
    # Order ticket for our stop order, Datetime when stop order was last hit
    stopMarketTicket = None
    stopMarketOrderFillTime = datetime.min
    highestSPYPrice = 0
    
    def Initialize(self):
        self.SetStartDate(2018, 12, 1)
        self.SetEndDate(2018, 12, 10)
        self.SetCash(100000)
        spy = self.AddEquity("SPY", Resolution.Daily)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)
        
    def OnData(self, data):
        
        if (self.Time - self.stopMarketOrderFillTime).days < 15:
            return

        if not self.Portfolio.Invested:
            self.MarketOrder("SPY", 500)
            self.stopMarketTicket = self.StopMarketOrder("SPY", -500, 0.9 * self.Securities["SPY"].Close)
        
        else:
            
            # 檢查最近的價錢是不是比最高價高
            #1. Check if the SPY price is higher that highestSPYPrice.
            if self.Securities["SPY"].Close > self.highestSPYPrice:
                
                # 如果是, 就把最高的價錢更新
                #2. Save the new high to highestSPYPrice; then update the stop price to 90% of highestSPYPrice 
                self.highestSPYPrice = self.Securities["SPY"].Close
                
                # 把stop price 設定在最高價的 9成
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = self.highestSPYPrice * 0.9
                self.stopMarketTicket.Update(updateFields)
                
                #3. Print the new stop price with Debug() 把最高和 SL 打印出來
                self.Debug("SPY: " + str(self.highestSPYPrice) + " Stop: " + str(updateFields.StopPrice))
                
    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status != OrderStatus.Filled:
            return
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketOrderFillTime = self.Time
            
