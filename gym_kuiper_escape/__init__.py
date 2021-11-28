from gym.envs.registration import register

register(
    id='kuiper-escape-easy-v0',
    entry_point='gym_kuiper_escape.envs:KuiperEscapeEasy',
)

register(
    id='kuiper-escape-medium-v0',
    entry_point='gym_kuiper_escape.envs:KuiperEscapeMedium',
)

register(
    id='kuiper-escape-hard-v0',
    entry_point='gym_kuiper_escape.envs:KuiperEscapeHard',
)