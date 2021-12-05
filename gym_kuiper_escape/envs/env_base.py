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
     - 2: Up/Right Diagnal
     - 3: Right
     - 4: Right/Down Diagnal
     - 5: Down
     - 6: Down/Left Diagnal
     - 7: Left
     - 8: Left/Up Diagnal

    The state/observation consists of the following variables:
     - Player Location: x, y
     - For N-nearest Asteroids:
        - Absolute position (x, y)
        - Straight line distance from player
        - Angle from player to asteroid
        - Size
        - Speed
        - Heading (i.e. is it headed at or away from player)

    Note: All state observations are normalized between 0 and 1

    The environment will provide the following rewards:
     - Reward of 1 for each step without losing life
     - Penalty (sized based on framerate) for each life lost

    """

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, mode='agent', lives_start=10):
        self.mode = mode
        self.lives_start = lives_start
        self.game = Game(mode=mode, lives=self.lives_start)
        self.iteration = 0
        self.iteration_max = 15 * 60 * self.game.framerate  # 15 minutes
        self.n_rock_state_obs = 10
        self.init_obs = self.get_state()
        self.action_space = Discrete(9)
        self.observation_space = Box(low=0, high=1, shape=(len(self.init_obs), 1), dtype=np.float16)
        self.reward_range = (-5 * self.game.framerate, 1)

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
        lives_before = self.game.player.lives
        self.game.step_frame(action)
        lives_after = self.game.player.lives
        self.iteration += 1

        # Gather observation
        observation = self.get_state()

        # Gather reward
        reward = 1
        if lives_after < lives_before:
            reward = -5 * self.game.framerate

        # Check stop conditions
        if lives_after == 0:
            done = True
        elif self.iteration > self.iteration_max:
            done = True
        else:
            done = False

        # Gather metadata/info
        info = {
            'iteration': self.iteration,
            'score': self.game.score, 
            'lives_before': lives_before,
            'lives_after': lives_after
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
        self.game = Game(mode='agent', lives=self.lives_start)
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
        state_player = self.get_player_state()
        state_rocks = self.get_rock_state()
        state_rocks = state_rocks.flatten()
        state = np.concatenate([state_player, state_rocks])
        state = state.astype(np.float16)
        return state

    def get_player_state(self):
        x, y = self.get_position(self.game.player)
        array_state_player = np.array([x, y])
        array_state_player = array_state_player.astype(np.float16)
        return array_state_player

    def get_rock_state(self):

        # Get rock states and sort by proximity
        ls_rock_states = []
        for rock in self.game.rocks.sprites():
            x, y = self.get_position(rock)
            x = x / self.game.screen_width
            y = y / self.game.screen_height
            dist_max = math.sqrt(self.game.screen_height**2 + self.game.screen_width**2)
            dist = self.get_rock_distance(rock) / dist_max
            rock_angle = self.get_rock_angle(rock) / 360
            size = rock.size / rock.size_max
            speed = rock.speed / rock.speed_max
            heading = (self.get_rock_heading(rock) / 360) + 0.5
            ls_rock_states.append([dist, x, y, rock_angle, size, speed, heading])
        ls_rock_states.sort()

        # Construct rock observation array
        n_rock_obs = 10
        array_state_rocks = np.zeros((self.n_rock_state_obs, 7))
        for i in range(n_rock_obs):
            try:
                array_state_rocks[i, :] = ls_rock_states[i]
            except:
                pass
        array_state_rocks = array_state_rocks.astype(np.float16)
        return array_state_rocks

    def get_position(self, sprite):
        center = sprite.rect.center
        x = round(center[0])
        y = self.game.screen_height - round(center[1])  # flip pygame coordnates
        return (x, y)

    def get_distance(self, sprite_1, sprite_2):
        x1, y1 = self.get_position(sprite_1)
        x2, y2 = self.get_position(sprite_2)
        return int(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

    def get_rock_distance(self, rock):
        return int(self.get_distance(self.game.player, rock))

    def get_angle(self, sprite_1, sprite_2):
        x1, y1 = self.get_position(sprite_1)
        x2, y2 = self.get_position(sprite_2)
        x_rel = x2 - x1
        y_rel = y2 - y1
        y_rel = y_rel
        angle = math.atan2(y_rel, x_rel)
        angle = math.degrees(angle) % 360
        return int(angle)

    def get_rock_angle(self, rock):
        return int(self.get_angle(self.game.player, rock))

    def get_rock_heading(self, rock):
        angle_speed = math.degrees(rock.angle)
        angle_player = self.get_angle(rock, self.game.player)
        angle_rel = angle_player - angle_speed
        if angle_rel > 180:
            angle_rel = angle_rel % 180 - 180
        if angle_rel < -180:
            angle_rel = angle_rel % 180
        return int(angle_rel)


if __name__ == "__main__":
    env = KuiperEscape(mode='human')
    env.game.play()
