import torch
from torch.distributions import Categorical 
from env import Environment
from ppo import PPO
import tqdm
import pandas as pd
import numpy as np
import warnings 
warnings.filterwarnings('ignore')

T_horizon = 60
date_log = []
value_log = []
action_log = []
reward_log = []

def main(model_name, risk_adverse, epochs = 100, transaction=0.0002):
    df = pd.read_csv("upbit_data\\train_data_2023.csv", index_col=0)
    if model_name=="ppo":
        model = PPO()

    for n_epi in tqdm.tqdm(range(epochs)):
        env = Environment(df, risk_adverse = risk_adverse, transaction=transaction)
        s = env.reset()
        
        h1_out = (torch.zeros([1, 1, 64], dtype=torch.float), torch.zeros([1, 1, 64], dtype=torch.float))
        h2_out = (torch.zeros([1, 1, 64], dtype=torch.float), torch.zeros([1, 1, 64], dtype=torch.float))
        
        s = np.array(s, dtype=np.float32)
        done = False
        date_list = []
        value_list = []
        action_list = []
        reward_list = []
        balance_list = []
        coin_list = []
        
        date = 0
        while not done:
            
            for t in range(T_horizon):
                h1_in = h1_out
                h2_in = h2_out
                
                prob, h1_out, h2_out = model.pi(torch.from_numpy(s).float(), h1_in, h2_in)
                
                prob = prob.view(-1)
                
                m = Categorical(prob)
                
                a = m.sample().item() # softmax에서 0~11의 값을 뱉어내므로 -5를 통해서 내가 설계한 action으로 만들어 준다. => 그 action의 인덱스를 바꿈
                s_prime, r, done, port_value, balance, coin = env.step(a)
                
                if r==None:
                    break
                
                date_list.append(s_prime.name)
                value_list.append(port_value)
                action_list.append(a)
                reward_list.append(r)
                balance_list.append(balance)
                coin_list.append(coin)
                
                model.put_data([np.array(s, dtype=np.float32),
                            a, r, \
                            np.array(s_prime, dtype=np.float32),\
                            prob[a].item(),\
                            h1_in, h1_out, h2_in, h2_out, done])

                s = np.array(s_prime, dtype=np.float32)
                    
                date += 1
                if date%3600==0:
                    log = pd.DataFrame([date_log, value_list, action_list, reward_list, balance_list, coin_list]).T
                    log.columns = ["date","value", "action", "reward", "balance", "coin"]
                    log.to_csv("log\\log_{}.csv".format(n_epi+1))
                    print(date)
            
                if done:
                    break
            
            model.train_net()
        
        log = pd.DataFrame([date_log, value_list, action_list, reward_list, balance_list, coin_list]).T
        log.columns = ["date","value", "action", "reward", "balance", "coin"]
        log.to_csv("log\\log_{}.csv".format(n_epi+1))
        
        print("# of episode :{} ".format(n_epi+1))
        
    print("#####")
    print("END")
    print("#####")
    

if __name__ == '__main__':
    main(model_name="ppo", risk_adverse=1.2, epochs=100, transaction=0.0000)