import torch
from torch.distributions import Categorical 
from env2 import Environment
from ppo2 import PPO2
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
    if model_name=="ppo2":
        model = PPO2()

    for n_epi in tqdm.tqdm(range(epochs)):
        env = Environment(df, risk_adverse = risk_adverse, transaction=transaction)
        state = env.reset()
        
        h1_out = (torch.zeros([1, 1, 64], dtype=torch.float), torch.zeros([1, 1, 64], dtype=torch.float))
        h2_out = (torch.zeros([1, 1, 64], dtype=torch.float), torch.zeros([1, 1, 64], dtype=torch.float))
        
        state = np.array(state, dtype=np.float32)
        done = False
        date_list = []
        value_list = []
        action_list = []
        reward_list = []
        balance_list = []
        coin_list = []
        position_list = []
        all_action_list  =[]
        
        date = 0
        while not done:
            
            for t in range(T_horizon):
                h1_in = h1_out
                h2_in = h2_out
                
                prob, h1_out, h2_out = model.pi(torch.from_numpy(state).float(), h1_in, h2_in)
                
                prob = prob.view(-1)
                
                action_distribition = Categorical(prob)
                
                action = action_distribition.sample().item() # softmax에서 0~11의 값을 뱉어냄
                env_step_dict = env.step(action)
                
                state_time = env_step_dict["state_time"]
                next_state = env_step_dict["next_state"]
                reward = env_step_dict["reward"]
                done = env_step_dict["done"]  
                portfolio_value = env_step_dict["portfolio_value"]  
                balance = env_step_dict["balance"]  
                bitcoin = env_step_dict["bitcoin"]
                position = env_step_dict["position"]  
                all_action = env_step_dict["action_list"] 
                
                if done:
                    break
                
                date_list.append(state_time)
                value_list.append(portfolio_value)
                action_list.append(action)
                reward_list.append(reward)
                balance_list.append(balance)
                coin_list.append(bitcoin)
                position_list.append(position)
                all_action_list.append(all_action)
                
                
                position_action = all_action_list[:]
                position_action.append(position)
                
                model.put_data([np.array(state, dtype=np.float32),
                            action, 
                            reward,
                            np.array(next_state, dtype=np.float32),\
                            prob[action].item(),\
                            h1_in, h1_out, h2_in, h2_out, done, position_action])

                s = np.array(next_state, dtype=np.float32)
                    
                date += 1
                if date%3600==0:
                    log = pd.DataFrame([date_log, value_list, action_list, reward_list, balance_list, coin_list, position_list]).T
                    log.columns = ["date","value", "action", "reward", "balance", "coin", "position"]
                    log.to_csv("log\\log_{}.csv".format(n_epi+1))
                    print(date)
            
                if done:
                    break
            
            model.train_net()
        
        log = pd.DataFrame([date_log, value_list, action_list, reward_list, balance_list, coin_list, position_list]).T
        log.columns = ["date","value", "action", "reward", "balance", "coin", "position"]
        log.to_csv("log\\log_{}.csv".format(n_epi+1))
        
        print("# of episode :{} ".format(n_epi+1))
        
    print("#####")
    print("END")
    print("#####")
    

if __name__ == '__main__':
    main(model_name="ppo2", risk_adverse=1.2, epochs=100, transaction=0.0000)