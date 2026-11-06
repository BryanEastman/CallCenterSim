from sim.sim_classes import *
from sim.generate_calls import *

import simpy

format_pattern = "%Y-%m-%d %H:%M:%S"
day_start = dt.strptime("2026-11-06 00:00:00", format_pattern)
day_end = day_start + timedelta(days=1)

start_timestamp: int = int(day_start.timestamp())
end_timestamp: int = int(day_end.timestamp())

day_len: int = end_timestamp - start_timestamp
day_mid = int(day_len / 2)


def run_sim() -> None:
    env = simpy.Environment()

    agent_1_schedule: list[tuple] = [
        (AgentState.OFFLINE, 0),
        (AgentState.AVAILABLE, 10),
        (AgentState.BREAK, 30),
        (AgentState.AVAILABLE, 35),
        (AgentState.LUNCH, 40),
        (AgentState.AVAILABLE, 45),
        (AgentState.BREAK, 50),
        (AgentState.AVAILABLE, 55),
        (AgentState.OFFLINE, 60),
    ]
    agent_2_schedule: list[tuple] = [
        (AgentState.OFFLINE, 0),
        (AgentState.AVAILABLE, 5),
        (AgentState.BREAK, 6),
        (AgentState.AVAILABLE, 7),
        (AgentState.LUNCH, 60),
        (AgentState.AVAILABLE, 61),
        (AgentState.BREAK, 62),
        (AgentState.AVAILABLE, 63),
        (AgentState.OFFLINE, 64),
    ]
    agents: list[Agent] = [
        Agent("id1", env, agent_1_schedule),
        Agent("id2", env, agent_2_schedule),
    ]
    seed = 4
    synthetic_call = generate_call_data(env, 50, 600, day_mid=day_mid, day_len=day_len)
    calls: list[Call] = [
        OutboundCall(env, "ob1", 5, 10),
        InboundCall(env, "ib1", 15, 15, 6),
        InboundCall(env, "ib2", 31, 15, 2),
    ] + synthetic_call

    CallCenter(env, agents, calls, day_end=end_timestamp)

    env.run()


def main() -> None:
    run_sim()
