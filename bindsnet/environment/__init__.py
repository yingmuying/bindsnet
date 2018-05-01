import os
import sys
import gym
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

from bindsnet.datasets.preprocess import *
from bindsnet.encoding            import *
from skimage.measure              import block_reduce


class Games(ABC):
	'''
	Abstract base class for OpenAI gym environments.
	'''
	def __init__(self):
		'''
		Abstract constructor for the Nodes class.
		'''
		super().__init__()

	@abstractmethod
	def pre_process(self):
		pass
	
	def get_observation(self):
		return self.obs

	def get_reward(self):
		return self.reward
	

class SpaceInvaders(Games):
	'''
	A wrapper around the SpaceInvaders-v0 OpenAI gym environment.
	'''
	def __init__(self, max_prob=0.25, diffs=True, encode_func=get_bernoulli):
		'''
		Initializes the OpenAI Gym Space Invaders environment wrapper.
		
		Inputs:
			max_prob (float): Specifies the maximum
				Bernoulli trial spiking probability.
			diffs (bool): Whether to record previous
				frame and take difference for new frame.
			encode_func (bindsnet.encoding): Encoding of spikes
		'''
		super().__init__()
		
		self.max_prob = max_prob
		self.env = gym.make('SpaceInvaders-v0')
		self.diffs = diffs
		self.encode = encode_func

	def step(self, a):
		'''
		Wrapper around the OpenAI Gym environment `step()` function.
		
		Inputs:
			a (int): Action to take in Space Invaders environment.
		
		Returns:
			obs (torch.Tensor): Observation from the environment.
			reward (float): Reward signal from the environment.
			done (bool): Indicates whether the simulation has finished.
			info (dict): Current information about the environment.
		'''
		# Call gym's environment step function.
		obs, reward, done, info = self.env.step(a)
		
		# Subsample and convert to torch.Tensor.
		#obs = block_reduce(obs, block_size=(3, 3, 3), func=np.mean)
		#obs = torch.from_numpy(obs).view(1, -1).float()
		
		obs = self.pre_process(obs)

		# Calculate difference and store previous frame.
#		if self.diffs:
#			obs = torch.clamp(obs - self.previous, 0, 1)
#			self.previous = obs
		
#		 convert to Bernoulli-distributed spikes.
		obs = next(self.encode(obs, max_prob=self.max_prob))
		
#		obs = self.get_input(obs)
		# Return converted observations and other information.
		return obs.view(1,-1), reward, done, info


	def reset(self):
		'''
		Wrapper around the OpenAI Gym environment `reset()` function.
		
		Returns:
			obs (torch.Tensor): Observation from the environment.
		'''
		# Call gym's environment reset function.
		obs = self.env.reset()
		
		# Subsample and convert to torch.Tensor.
#		obs = block_reduce(obs, block_size=(3, 3, 3), func=np.mean)
#		obs = torch.from_numpy(obs).view(1, -1).float()

		obs = self.pre_process(obs)
		
		# Store previous frame.
		if self.diffs:
			self.previous = obs
		
		# Convert to Bernoulli-distributed spikes.
		obs = next(self.encode(obs, max_prob=self.max_prob))
		
		# Return converted observations.
		return obs

	def render(self):
		'''
		Wrapper around the OpenAI Gym environment `render()` function.
		'''
		self.env.render()

	def close(self):
		'''
		Wrapper around the OpenAI Gym environment `close()` function.
		'''
		self.env.close()

	def pre_process(self, obs):
		'''
		Pre-Processing step for a state specific to Space Invaders.
		
		Inputs:
			obs(numpy.array): Observation from the environment.
		
		Returns:
			obs (torch.Tensor): Pre-processed observation.
		'''
		obs = subsample( gray_scale(obs), 84, 110 )
		obs = obs[26:104, :]
		obs = binary_image(obs)
		
#		fig = plt.figure()
#		plt.imshow(obs, interpolation='nearest')
#		fig.savefig(r'/mnt/c/Users/Hassaan/Desktop/School related/Spring 2018/Independent Study')
#		sys.exit()

		obs = np.reshape(obs, (78, 84, 1))
		obs = torch.from_numpy(obs).view(1, -1).float()
		return obs
		
class CartPole(Games):
	'''
	A wrapper around the CartPole-v0 OpenAI gym environment.
	'''
	def __init__(self, max_prob=0.5):
		'''
		Initializes the OpenAI Gym Space Invaders environment wrapper.
		
		Inputs:
			max_prob (float): Specifies the maximum
				Bernoulli trial spiking probability.
		'''
		super().__init__()
		
		self.max_prob = max_prob
		self.env = gym.make('CartPole-v0')

	def step(self, a):
		'''
		Wrapper around the OpenAI Gym environment `step()` function.
		
		Inputs:
			a (int): Action to take in Space Invaders environment.
		
		Returns:
			(torch.Tensor): Observation from the environment.
			(float): Reward signal from the environment.
			(bool): Indicates whether the simulation has finished.
			(dict): Current information about the environment.
		'''
		# Call gym's environment step function.
		obs, reward, done, info = self.env.step(a)
		
		# Encoding into positive values.
		obs = np.array([obs[0] + 2.4,
						-min(obs[1], 0),
						max(obs[1], 0),
						obs[2] + 41.8,
						-min(obs[3], 0),
						max(obs[3], 0)])
		
		# Convert to torch.Tensor, and
		# convert to Bernoulli-distributed spikes.
		obs = torch.from_numpy(obs).view(1, -1).float()
		obs = get_bernoulli(obs, max_prob=self.max_prob)
		
		# Return converted observations and other information.
		return next(obs).view(1, -1), reward, done, info

	def reset(self):
		'''
		Wrapper around the OpenAI Gym environment `reset()` function.
		
		Returns:
			(torch.Tensor): Observation from the environment.
		'''
		# Call gym's environment reset function.
		obs = self.env.reset()
		
		# Encoding into positive values.
		obs = np.array([obs[0] + 2.4,
						-min(obs[1], 0),
						max(obs[1], 0),
						obs[2] + 41.8,
						-min(obs[3], 0),
						max(obs[3], 0)])
		
		# Convert to torch.Tensor, and
		# convert to Bernoulli-distributed spikes.
		obs = torch.from_numpy(obs).view(1, -1).float()
		obs = get_bernoulli(obs, max_prob=self.max_prob)

		# Return converted observations.
		return next(obs)

	def pre_process(self):
		pass
	
	def render(self):
		'''
		Wrapper around the OpenAI Gym environment `render()` function.
		'''
		self.env.render()

	def close(self):
		'''
		Wrapper around the OpenAI Gym environment `close()` function.
		'''
		self.env.close()