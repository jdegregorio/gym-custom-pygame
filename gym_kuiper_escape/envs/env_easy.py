
import sys
import gym
from gym import error, spaces, utils
from gym.utils import seeding
import math
import pygame

sys.path.append('./kuiper_escape')
from game import Game

class KuiperEscapeEasy(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, mode='agent', lives=10):
        self.mode = mode
        self.game = Game(mode=mode, lives=lives)
        self.iteration = 0
        self.iteration_max = 15 * 60 * self.game.framerate  # 15 minutes
        self.n_rock_state_obs = 10

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

        return observation, reward, done, info

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
        self.game = Game(mode='agent')
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
            rgb_array = pygame.surfarray.array3d()
            rgb_array = rgb_array.astype(np.uint8)
            rgb_array = np.rot90(rgb_array)
            rgb_array = np.flip(rgb_array)
            rgb_array = np.fliplr(rgb_array)
            return rgb_array
    
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
    env = KuiperEscapeEasy(mode='human')
    env.game.play()
