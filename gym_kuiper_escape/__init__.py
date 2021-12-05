from gym.envs.registration import register

register(
    id='kuiper-escape-base-v0',
    entry_point='gym_kuiper_escape.envs:KuiperEscape',
)