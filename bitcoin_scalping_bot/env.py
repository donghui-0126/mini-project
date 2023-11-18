class Environment:
    """
    action의 종류
        - BUY: 가진 현금에서 [100%,50%,25%,10%,5%] 매수
        - SELL: 가진 주식에서 [100%,50%,25%,10%,5%] 매도
        - HOLD: DO NOTHING
        
    action = 6 => 5% 매수 
    action = 7 => 10% 매수 
    action = 8 => 25% 매수 
    action = 9 => 50% 매수 
    action = 10 => 100% 매수 
    
    action = 0 => 5% 매도 
    action = 1 => 10% 매도 
    action = 2 => 25% 매도 
    action = 3 => 50% 매도 
    action = 4 => 100% 매도
    
    action = 5 => Hoding 
    
    """
    # mid price = (high + low) / 2
    PCT_IDX = -3 # 1분전 MID price의 가격 변동 
    PCT_SIGN_IDX = -2 # 1분전 MID price의 가격 변동 부호
    MID_IDX = -1
    
    def __init__(self, chart_data=None, risk_adverse= 1.3 ,stop_trade=0.9 ,balance=100000000, transaction=0.0005, goalpct_per_hour=0.05):
        self.chart_data = chart_data
        self.idx = 0

        
        self.risk_adverse = risk_adverse # 손실에 주는 가중치 
        self.stop_trade = stop_trade # 손절선
        self.transaction = transaction # 거래수수료
        
        self.current_state = chart_data.iloc[self.idx]
        self.next_state = chart_data.iloc[self.idx+1]
                    
        self.current_price = self.chart_data.iloc[self.idx, self.MID_IDX]
        self.next_price = self.chart_data.iloc[self.idx+1, self.MID_IDX]
        
        self.balance = [balance]  # 포트폴리오가 보유한 현금
        self.bitcoin = [0]  # 포트폴리오가 보유한 비트코인의 가치 (매 거래마다 바로 청산됨)
        self.portfolio_value = [balance]
        self.action_list = [5]
        self.transaction_list = [0.25,0.5,1,2,3,0,0.25,0.5,1,2,3]
        
    def reset(self):
        self.idx = 0
        state = self.chart_data.iloc[self.idx]
        return state
    
    def step(self, action):
        self.current_state = self.chart_data.iloc[self.idx]
        self.next_state = self.chart_data.iloc[self.idx+1]
        self.current_price = self.chart_data.iloc[self.idx, self.MID_IDX]
        self.next_price = self.chart_data.iloc[self.idx+1, self.MID_IDX]



        current_value = self.balance[-1] + self.bitcoin[-1]*self.current_price
        self.portfolio_value.append(current_value)
        
        
        # 학습이 끝나거나 만약 시드의 self.stop_trade%를 잃는다면 손절 
        if ((self.chart_data).shape[0] > self.idx+1) and (self.portfolio_value[0]*self.stop_trade <= self.portfolio_value[-1]):
            s_prime = self.chart_data.iloc[self.idx+1]
            reward = self.get_reward(action) * 100 # -1~1 사이의 loss값이 나오도록 적절하게 scaling
            done = False
            self.idx += 1

            self.action_list.append(action)
            
            if reward>=0:
                return (s_prime, reward, done, self.portfolio_value[-1])
            else:
                return (s_prime, reward * self.risk_adverse, done, self.portfolio_value[-1])

        else:
            print("#########################################################################")
            print(f'{self.next_state.name}에서 {self.portfolio_value[-1]}으로 trading stop')
            return (self.next_state, -1, True, self.portfolio_value[-1]) 
            
    def get_reward(self, action):
        """
        action은 다음 타임스텝의 행동(매수, 매도, 홀드)을 의미한다. 
        """
        
        """     
        손실에 더 큰 penalty(risk adverse)를 줌으로써, 손실 회피형 Agent를 구성가능 
        근데 이러면, 장기적인 보상에 대해서는 감지를 잘 못하지 않나...?
        
            => GAE가 이 의문을 해결해준다고 생각함. n-step TD를 통해서 미래의 보상을 고려할 수 있음. 
            
        """        
        
        # BUY
        if action >= 6:
            # 보유 현금 25% 매수
            if action == 6:
                buy_ratio = 0.25
                buy_budget = self.balance[-1] * buy_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] - buy_budget + clearing_budget - (buy_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(buy_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * buy_ratio - self.transaction_list[self.action_list[-1]]
                return reward
            
            # 보유 현금 50% 매수
            elif action == 7:
                buy_ratio = 0.5
                buy_budget = self.balance[-1] * buy_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] - buy_budget + clearing_budget - (buy_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(buy_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * buy_ratio - self.transaction_list[self.action_list[-1]]
                return reward
                        
            # 보유 현금 100% 매수
            elif action == 8:
                buy_ratio = 1
                buy_budget = self.balance[-1] * buy_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] - buy_budget + clearing_budget - (buy_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(buy_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * buy_ratio - self.transaction_list[self.action_list[-1]]
                return reward
            
            # 보유 현금 200% 매수
            elif action == 9:
                buy_ratio = 2
                buy_budget = self.balance[-1] * buy_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] - buy_budget + clearing_budget - (buy_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(buy_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * buy_ratio - self.transaction_list[self.action_list[-1]]
                return reward
            
            # 보유 현금 300% 매수
            elif action == 10:
                buy_ratio = 3
                buy_budget = self.balance[-1] * buy_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] - buy_budget + clearing_budget - (buy_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(buy_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * buy_ratio - self.transaction_list[self.action_list[-1]]
                return reward
            
            
        # SELL
        elif action <= 4:
            # 보유 현금의 25% 공매도
            if action == 0:
                sell_ratio = 0.25
                sell_budget = self.balance[-1] * sell_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] + sell_budget + clearing_budget - (sell_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(-sell_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * sell_ratio - self.transaction_list[self.action_list[-1]]
                return reward
            
            # 보유 coin의 50% 공매도
            if action == 1:
                sell_ratio = 0.5
                sell_budget = self.balance[-1] * sell_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] + sell_budget + clearing_budget - (sell_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(-sell_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * sell_ratio - self.transaction_list[self.action_list[-1]]
                return reward

            # 보유 coin의 100% 공매도
            if action == 2:
                sell_ratio = 1
                sell_budget = self.balance[-1] * sell_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] + sell_budget + clearing_budget - (sell_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(-sell_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * sell_ratio - self.transaction_list[self.action_list[-1]]
                return reward

            # 보유 coin의 200% 공매도
            if action == 3:
                sell_ratio = 2
                sell_budget = self.balance[-1] * sell_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] + sell_budget + clearing_budget - (sell_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(-sell_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * sell_ratio - self.transaction_list[self.action_list[-1]]
                return reward
            
            # 보유 coin의 300% 공매도
            if action == 4:
                sell_ratio = 3
                sell_budget = self.balance[-1] * sell_ratio
                clearing_budget = self.bitcoin[-1] * self.current_price
                self.balance.append(self.balance[-1] + sell_budget + clearing_budget - (sell_budget+abs(clearing_budget))*self.transaction)
                self.bitcoin.append(-sell_budget/self.current_price)  
        
                reward = (self.next_state.iloc[self.PCT_IDX]-self.transaction) * sell_ratio - self.transaction_list[self.action_list[-1]]
                return reward
        
        
        elif action == 5:
            reward = -abs(self.next_state.iloc[self.PCT_IDX])/2   
            return reward
        
