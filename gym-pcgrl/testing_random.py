import gym
import gym_pcgrl

env = gym.make('zelda-narrow-v0')
obs = env.reset()
for t in range(20):
  action = env.action_space.sample()
  obs, reward, done, info = env.step(action)
  env.render('human')
  if done:
    print("Episode finished after {} timesteps".format(t+1))
    for i in range(10000000000000000):
        #print(env)
        continue
    #break