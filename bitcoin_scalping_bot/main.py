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
total_portfolio_value = []

def main():
    df = pd.read_csv("upbit_data\\train_data_2023.csv", index_col=0)
    env = Environment(df)
    model = PPO()
    score = 0.0
    print_interval = 20

    for n_epi in tqdm.tqdm(range(100)):
        s = env.reset()
        h_out = (torch.zeros([1, 1, 64], dtype=torch.float), torch.zeros([1, 1, 64], dtype=torch.float))
        s = np.array(s, dtype=np.float32)
        done = False
        portfolio_value_list = []
        date = 0
        while not done:
            for t in range(T_horizon):
                h_in = h_out
                
                prob, h_out = model.pi(torch.from_numpy(s).float(), h_in)
                
                prob = prob.view(-1)
                
                m = Categorical(prob)
                
                a = m.sample().item() # softmax에서 0~11의 값을 뱉어내므로 -5를 통해서 내가 설계한 action으로 만들어 준다. => 그냥 action의 인덱스를 바꿈
                s_prime, r, done, port_value = env.step(a)
                
                if r==None:
                    break
                
                portfolio_value_list.append(port_value)
                
                prob_pre_action = torch.tensor(prob)

                model.put_data([np.array(s, dtype=np.float32),
                            a, r, \
                            np.array(s_prime, dtype=np.float32),\
                            prob[a].item(),\
                            h_in, h_out, done])

                s = np.array(s_prime, dtype=np.float32)
                
                date += 1
                
                if date//720 == 0:
                    print(port_value)    
            
                if done:
                    break
            
            model.train_net()
            
        total_portfolio_value.append(portfolio_value_list)

        print("# of episode :{} ".format(n_epi))
        print(portfolio_value_list)
        
    print("#####")
    print("END")
    print("#####")

if __name__ == '__main__':
    main()
