import gym
import gym_pcgrl

#env = gym.make('sokoban-narrow-v0')

env2 = gym.make('angrybirds-wide-v0')
#env2 = gym.make('zelda-wide-v0')
#env3 = gym.make('angrybirds-narrow-v0')

obs = env2.reset()
#obs2 = env3.reset()

i=0
for t in range(100):
  env2.render()
  #env3.render()
  i += 1

for t in range(10):
  action = env2.action_space.sample()
  obs, reward, done, info = env2.step(action)
  env2.render('human')
  if done:
    print("Episode finished after {} timesteps".format(t+1))
    break


