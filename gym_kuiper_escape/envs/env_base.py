# Standard imports
import sys
import os
import math

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

    The state/observation consists of the following variables: TODO

    The environment will provide the following rewards:
     - Reward of 1 for each frame without dying.
     - Reward not awareded if player is in corners

    """

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(
        self, 
        mode='agent',
        lives_start=1,
        rock_rate_start=1,
        rock_rate_increment=1e6,
        rock_size_min=50,
        rock_size_max=50,
        rock_speed_min=5,
        rock_speed_max=5
    ):
        self.mode = mode
        self.output_size=128
        self.lives_start = lives_start
        self.rock_rate_start=rock_rate_start
        self.rock_rate_increment=rock_rate_increment
        self.rock_size_min=rock_size_min
        self.rock_size_max=rock_size_max
        self.rock_speed_min=rock_speed_min
        self.rock_speed_max=rock_speed_max
        self.game = Game(
            mode=self.mode,
            lives=self.lives_start, 
            rock_rate_start=self.rock_rate_start,
            rock_rate_increment=self.rock_rate_increment,
            rock_size_min=self.rock_size_min,
            rock_size_max=self.rock_size_max,
            rock_speed_min=self.rock_speed_min,
            rock_speed_max=self.rock_speed_max
        )
        self.iteration = 0
        self.iteration_max = 15 * 60 * self.game.framerate  # 15 minutes
        self.init_obs = self.get_state()
        self.action_space = Discrete(5)
        self.observation_space = Box(low=0, high=255, shape=(self.output_size, self.output_size, 3), dtype=np.float16)
        self.reward_range = (0, 1)

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
        xp, yp = self.get_position(self.game.player)
        xp = xp / self.game.screen_width
        yp = yp / self.game.screen_height
        dist_from_center = math.sqrt((xp-0.5)**2 + (yp-0.5)**2)
        if dist_from_center < 0.35:
            reward = 1
        else:
            reward = 0

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
            'score': self.game.score
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
        self.game = Game(
            mode=self.mode,
            lives=self.lives_start, 
            rock_rate_start=self.rock_rate_start,
            rock_rate_increment=self.rock_rate_increment,
            rock_size_min=self.rock_size_min,
            rock_size_max=self.rock_size_max,
            rock_speed_min=self.rock_speed_min,
            rock_speed_max=self.rock_speed_max
        )
        self.iteration = 0
        observation = self.get_state()
        return observation

    def render(self, mode='human'):
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
            self.game.render_screen()
            self.game.clock.tick(self.game.framerate)

        if mode == 'rgb_array':
            surf = pygame.display.get_surface()
            rgb_array = pygame.surfarray.array3d(surf)
            rgb_array = rgb_array.astype(np.uint8)
            rgb_array = np.rot90(rgb_array)
            rgb_array = np.flip(rgb_array)
            rgb_array = np.fliplr(rgb_array)
            return rgb_array
    
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

    def get_state(self):
        return self.get_rgb_state()

    # def get_state(self):
    #     self.grid = np.zeros((self.output_size, self.output_size))
    #     for rock in self.game.rocks.sprites():
    #         xr, yr = self.get_position(rock)
    #         size = rock.size / rock.size_max
    #         self.update_grid(xr, yr, size)
    #     xp, yp = self.get_position(self.game.player)
    #     self.update_grid(xp, yp, -1)
    #     return self.grid

    # def update_grid(self, x, y, value):
    #     ratio = self.output_size / self.game.screen_height
    #     x = int(x * ratio)
    #     y = int(y * ratio)
    #     self.grid[x, y] = value

    def get_rgb_state(self):
        surf = pygame.display.get_surface()
        array = pygame.surfarray.array3d(surf).astype(np.uint8)
        array.astype(np.float16)
        bin_size = int(self.game.screen_height / self.output_size)
        array = array.reshape((self.output_size, bin_size, self.output_size, bin_size, 3)).max(3).max(1)
        array = array.astype(np.uint8)
        return array

    def get_position(self, sprite):
        center = sprite.rect.center
        x = round(center[0])
        y = self.game.screen_height - round(center[1])  # flip pygame coordnates
        return (x, y)


if __name__ == "__main__":
    env = KuiperEscape(mode='human')
    env.game.play()
