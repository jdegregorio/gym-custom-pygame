# Custom OpenAI Gym Environment

## Overview 
This package unites the **PyGame Framework** with the **Open AI Gym Framework** to build a custom environment for training reinforcement learning models. Specifically, it implements the custom-built "Kuiper Escape" game.

## Custom Gym Environment

### Game Overview - Kuiper Escape

The objective of the game is to live as long as you can, while avoiding the asteroids in the Kuiper Belt. The player starts centered in the screen, an can move in any direction using the keyboard arrows.  Asteroids are generated with random sizes, speeds, and starting locations. The game ends once all player lives have expired.

`TODO: Insert image of game`

### Actions 

The user has the following discrete actions:
 * 0: Don't move
 * 1: Up
 * 2: Up/Right Diagnal
 * 3: Right
 * 4: Right/Down Diagnal
 * 5: Down
 * 6: Down/Left Diagnal
 * 7: Left
 * 8: Left/Up Diagnal

### State/Observations

The state/observation consists of the following variables:
 * Player Location: x, y
 * For N*nearest Asteroids:
 * Absolute position (x, y)
 * Straight line distance from player
 * Angle from player to asteroid
 * Size
 * Speed
 * Heading (i.e. is it headed at or away from player)

Note: All state observations are normalized between 0 and 1

### Rewards

The environment will provide the following rewards:
 * Reward of 1 for each step without losing life
 * Penalty (sized based on framerate) for each life lost


## Setup

### Installation
First it is recommended to setup a virtual environment:
```bash
python -m venv .env
source .env/bin/activate
```

Update pip and wheel to ensure a smooth installation process:
```bash
pip install --upgrade pip
pip install --upgrade wheel
```

Finally, install package locally with pip:
```bash
git clone https://github.com/jdegregorio/gym-kuiper-escape.git
pip install -e gym-kuiper-escape
```

To uninstall, use the following:
```bash
pip uninstall gym-kuiper-escape
```

### Development Environment Details
 * Python Version: 3.8.10
 * Operating System: Ubuntu 20.04.3 LTS


### How to Play Manually

To play the game without installing the package, run the following at the command line:

```bash
git clone https://github.com/jdegregorio/gym-kuiper-escape.git
cd gym-kuiper-escape
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python gym_kuiper_escape/envs/env_base.py
```

To play after installing the package, enter the following python commands:

```python
import gym
import gym_kuiper_escape
env = gym.make('kuiper-escape-base-v0', mode='human'))
env.game.play()
```
`TODO: Make manual play more user friendly`

## Reinforcement Learning
`TODO: Link to repo with RL experiments`


## Background & Resources

### Open AI Gym Framework
Open AI Gym provides a standardized framework for training reinforcement learning models. The framework has numerous built-in environments (often games) for experimentation, but also enables users to define their own custom environments.

 * [Open AI Gym Documentation](https://gym.openai.com/docs/)
 * [Creating Customer Environments](https://github.com/openai/gym/blob/master/docs/creating_environments.md)
 * [Example Custom Environment](https://github.com/openai/gym-soccer/blob/master/gym_soccer/envs/soccer_env.py)
 * [Core Open AI Gym Clases](https://github.com/openai/gym/blob/master/gym/core.py)

### PyGame Framework

PyGame is a framework for developing games within python. 

This [tutorial](https://realpython.com/pygame-a-primer/) is a great primer for getting started.
