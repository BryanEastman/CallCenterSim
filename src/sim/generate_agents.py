# schedule config

# each agent gets 2 30 minute breaks, 1 1 hour lunch
# 8 hour shifts
# configure first with timestrings and convert
# to get roughly the distribution of agents I want:
# 2 alt schedules per shift:
# 4 total shifts
# break 1: 2 or 2.5 hours after start
# lunch 4 or 5 hours after start
# break 2: 6 or 6.5 hours after start


from datetime import datetime as dt, timedelta
from datetime import time
from sim.sim_classes import AgentState, Agent
import math
from simpy import Environment


# TODO: remove these placeholders
format_pattern = "%Y-%m-%d %H:%M:%S"
day_start = dt.strptime("2026-11-06 00:00:00", format_pattern)
day_end = day_start + timedelta(days=1)

start_timestamp: int = int(day_start.timestamp())
end_timestamp: int = int(day_end.timestamp())

day_len: int = end_timestamp - start_timestamp
day_mid = int(day_len / 2)


def time_to_seconds(t: time, day: int) -> int:
    return t.hour * 3600 + t.minute * 60 + t.second + day


def build_shift(shift_start: time, shift_alt: bool) -> list[tuple[AgentState, int]]:
    shift_start_seconds: int = time_to_seconds(shift_start, day=start_timestamp)
    is_alt = 1 if shift_alt else 0

    break_1 = shift_start_seconds + 2 * 3600 + (60 * 30) * is_alt
    break_1_end = break_1 + 60 * 30
    lunch = shift_start_seconds + 4 * 3600 + (3600) * is_alt
    lunch_end = lunch + 3600
    break_2 = shift_start_seconds + 6 * 3600 + (60 * 30) * is_alt
    break_2_end = break_2 + 60 * 30
    shift_end = shift_start_seconds + 8 * 3600

    shift_tuple = [
        (AgentState.OFFLINE, 0),
        (AgentState.AVAILABLE, break_1_end),
        (AgentState.BREAK, break_1),
        (AgentState.AVAILABLE, shift_start_seconds),
        (AgentState.LUNCH, lunch),
        (AgentState.AVAILABLE, lunch_end),
        (AgentState.BREAK, break_2_end),
        (AgentState.AVAILABLE, shift_start_seconds),
        (AgentState.OFFLINE, shift_end),
    ]

    return shift_tuple


# take a fixed number of agents and evenly distribute shifts by 4 blocks, each with an alt break
# TODO: refactor this, no more hardcoding shift rules
def distribute_agents_by_schedule(n_agents: int, env: Environment) -> list[Agent]:
    agents_per_shift = math.floor(n_agents / 8)
    print("building agents")
    shift_1 = time(8, 0, 0)
    shift_2 = time(10, 0, 0)
    shift_3 = time(11, 30, 0)
    shift_4 = time(13, 0, 0)

    counter = 0
    agent_list: list[Agent] = []

    # I don't really care how this looks on paper
    for shift in [shift_1, shift_2, shift_3, shift_4]:
        for tf in [True, False]:
            for n in range(0, agents_per_shift):
                agent_list.append(
                    Agent(f"synth_agent_{counter}", env, build_shift(shift, tf))
                )
                counter += 1

    return agent_list
