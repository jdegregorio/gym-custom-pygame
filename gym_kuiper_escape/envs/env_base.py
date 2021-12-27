# Standard imports
import sys
import os
import math
import random

# 3rd party imports
import numpy as np
import gym
from gym.utils import seeding
from gym.spaces import Discrete, Box
import pygame

# Local imports
path_game = os.path.dirname(os.path.realpath(__file__)) + '/kuiper_escape'
sys.path.insert(0, path_game)
from game import Game
from lidar import Lidar


class KuiperEscape(gym.Env):
    """ Custom PyGame OpenAI Gym Environment - Kuiper Escape

    The objective of the game is to live as long as you can, while avoiding the
    asteroids in the Kuiper Belt.  Asteroids are generated with random sizes,
    speeds, and starting locations. The environment will exit once the max-time
    is elapsed, or once all player lives have expired.

    The user has the following discrete actions:
     - 0: Don't move
     - 1: Up
     - 2: Right
     - 3: Down
     - 4: Left
     - 5: Up/Right Diagnal (optional)
     - 6: Right/Down Diagnal (optional)
     - 7: Down/Left Diagnal (optional)
     - 8: Left/Up Diagnal (optional)

     Note: For actions 0-4 (none/up/right/down/left) are recommended for
     simplified action space.

    The state/observation is a "virtual" lidar system. It sends off virtual
    beams of light in all directions to gather an array of points describing
    the distance and characteristics of nearby objects. The observation data
    consists of "n" designated lidar beams (sent of in uniformally distributed
    angles), as well as n collision type flags (0 for no collision, or 1 for
    rock collision).

    The environment will provide the following rewards:
     - Reward of 1 for each frame without dying.
     - Reward not awareded if player is in corners

    """

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(
        self, 
        mode='agent',
        lives_start=1,
        player_speed=0.5,
        rock_rate=2,
        rock_speed_min=0.03,
        rock_speed_max=0.20,
        rock_size_min=0.05,
        rock_size_max=0.2,
        penalty_offcenter_val=0,
        penalty_offcenter_thres = 0.35,
        penalty_movement=0,
        framerate=30,
        output_size=64
    ):
        self.mode = mode
        self.output_size = output_size
        self.lives_start = lives_start
        self.player_speed = player_speed
        self.rock_rate = rock_rate
        self.rock_size_min = rock_size_min
        self.rock_size_max = rock_size_max
        self.rock_speed_min = rock_speed_min
        self.rock_speed_max = rock_speed_max
        self.penalty_offcenter_val = penalty_offcenter_val
        self.penalty_offcenter_thres = penalty_offcenter_thres
        self.penalty_movement = penalty_movement
        self.framerate = framerate
        self.game = self.init_game()
        self.lidar_n_beams = 64
        self.lidar_step_pct = 0.01
        self.lidar_max_radius_pct = 0.75
        self.lidar = self.init_lidar()
        self.iteration = 0
        self.iteration_max = 15 * 60 * self.game.framerate  # 15 minutes
        self.init_obs = self.get_state()
        self.action_space = Discrete(9)
        self.observation_space = Box(low=0, high=1, shape=(self.lidar_n_beams * 2, 1), dtype=np.float16)
        self.reward_range = (0, 1)

    def init_game(self):
        game = Game(
            mode=self.mode,
            lives=self.lives_start, 
            player_speed=self.player_speed,
            rock_rate=self.rock_rate,
            rock_speed_min=self.rock_speed_min,
            rock_speed_max=self.rock_speed_max,
            rock_size_min=self.rock_size_min,
            rock_size_max=self.rock_size_max,
            framerate=self.framerate
        )
        return game

    def init_lidar(self):
        lidar = Lidar(
            x = self.game.player.x,
            y = self.game.player.y,
            n_beams = self.lidar_n_beams,
            step = self.lidar_step_pct * self.game.screen_size,
            max_radius = self.lidar_max_radius_pct * self.game.screen_size,
            screen_size=self.game.screen_size
        )
        return lidar

    def step(self, action):
        """Run one timestep of the environment's dynamics. When end of
        episode is reached, you are responsible for calling `reset()`
        to reset this environment's state.
        Accepts an action and returns a tuple (observation, reward, done, info).
        Args:
            action (object): an action provided by the agent
        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (bool): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """

        # Step frame
        self.game.step_frame(action)
        self.iteration += 1

        # Gather observation
        observation = self.get_state()

        # Gather reward
        reward = self.get_reward(action)

        # Check stop conditions
        if self.game.player.lives == 0:
            done = True
        elif self.iteration > self.iteration_max:
            done = True
        else:
            done = False

        # Gather metadata/info
        info = {
            'iteration': self.iteration,
            'time': self.game.time
        }

        return (observation, reward, done, info)

    def reset(self):
        """Resets the environment to an initial state and returns an initial
        observation.
        Note that this function should not reset the environment's random
        number generator(s); random variables in the environment's state should
        be sampled independently between multiple calls to `reset()`. In other
        words, each call of `reset()` should yield an environment suitable for
        a new episode, independent of previous episodes.
        Returns:
            observation (object): the initial observation.
        """
        self.game = self.init_game()
        self.lidar = self.init_lidar()
        self.iteration = 0
        observation = self.get_state()
        return observation

    def render(self, mode, render_lidar=False):
        """Renders the environment.
        The set of supported modes varies per environment. (And some
        environments do not support rendering at all.) By convention,
        if mode is:
        - human: render to the current display or terminal and
            return nothing. Usually for human consumption.
        - rgb_array: Return an numpy.ndarray with shape (x, y, 3),
            representing RGB values for an x-by-y pixel image, suitable
            for turning into a video.
        - ansi: Return a string (str) or StringIO.StringIO containing a
            terminal-style text representation. The text can include newlines
            and ANSI escape sequences (e.g. for colors).
        Note:
            Make sure that your class's metadata 'render.modes' key includes
                the list of supported modes. It's recommended to call super()
                in implementations to use the functionality of this method.
        Args:
            mode (str): the mode to render with
        Example:
        class MyEnv(Env):
            metadata = {'render.modes': ['human', 'rgb_array']}
            def render(self, mode='human'):
                if mode == 'rgb_array':
                    return np.array(...) # return RGB frame suitable for video
                elif mode == 'human':
                    ... # pop up a window and render
                else:
                    super(MyEnv, self).render(mode=mode) # just raise an exception
        """
        if mode == 'human':
            self.game.turn_on_screen()
            self.game.update_screen()
            ls_beams = self.lidar.get_beams()
            if render_lidar:
                for beam in ls_beams:
                    self.game.screen.blit(beam.surf, beam.rect)
            self.game.render_screen()
            self.game.clock.tick(self.game.framerate)

        if mode == 'rgb_array':
            return self.get_rgb_array()
    
    def close(self):
        """Override close in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        pass

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator(s).
        Note:
            Some environments use multiple pseudorandom number generators.
            We want to capture all such seeds used in order to ensure that
            there aren't accidental correlations between multiple generators.
        Returns:
            list<bigint>: Returns the list of seeds used in this env's random
              number generators. The first value in the list should be the
              "main" seed, or the value which a reproducer should pass to
              'seed'. Often, the main seed equals the provided 'seed', but
              this won't be true if seed=None, for example.
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_reward(self, action):

        # Initialize with reward of 1 and penalty of 0
        reward = 1
        penalty = 0

        # Calculate penalty for distance from center
        xp = self.game.player.x
        yp = self.game.player.y
        xp = xp / self.game.screen_size
        yp = yp / self.game.screen_size
        dist_from_center = math.sqrt((xp-0.5)**2 + (yp-0.5)**2)
        if dist_from_center > self.penalty_offcenter_thres:
            penalty += self.penalty_offcenter_val

        # Calculate penalty for excessive movement
        if action != 0:
            penalty += self.penalty_movement

        # Adjust reward for penalties
        reward -= penalty
        reward = max([reward, 0])

        return reward

    def get_state(self):
        self.lidar.sync_position(self.game.player)
        ls_radius, ls_collide = self.lidar.scan(
            collide_sprites=self.game.rocks
        )
        array_radius = np.array(ls_radius)
        array_radius = array_radius / (self.lidar_max_radius_pct * self.game.screen_size)
        array_collide = np.array(ls_collide)
        array_state = np.concatenate([array_radius, array_collide])
        array_state = array_state.reshape((len(array_state), 1))
        return array_state
        
    def get_rgb_state(self):
        rgb_array = self.get_rgb_array()
        rgb_array = self.down_sample_rgb_array(rgb_array, self.output_size)
        rgb_array = rgb_array[:, :, 0]
        rgb_array = np.reshape(rgb_array, (self.output_size, self.output_size, 1))
        rgb_array = rgb_array.astype(np.uint8)
        return rgb_array

    def get_rgb_array(self):
        surf = pygame.display.get_surface()
        array = pygame.surfarray.array3d(surf).astype(np.float16)
        array = np.rot90(array)
        array = np.flip(array)
        array = np.fliplr(array)
        array = array.astype(np.uint8)
        return array

    def down_sample_rgb_array(self, array, output_size):
        bin_size = int(self.game.screen_size / output_size)
        array_ds = array.reshape((output_size, bin_size, output_size, bin_size, 3)).max(3).max(1)
        return array_ds


if __name__ == "__main__":

    env = KuiperEscape(
        mode='human',
        player_speed=0.5,
        rock_rate=1,
        rock_speed_min=0.05,
        rock_speed_max=0.10,
        rock_size_min=0.05,
        rock_size_max=0.10,
        framerate=10
    )
    env.game.play()
