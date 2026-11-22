from datetime import datetime as dt
from sim.sim_classes import *
from sim.generate_calls import *
from sim.generate_agents import *
import polars as pl
import itertools
from pathlib import Path
import os

import simpy

export_root = Path(str(os.getenv("EXPORT_ROOT")))


def run_sim(day_start: dt) -> CallCenter:

    day_end = day_start + timedelta(days=1)

    tcpa_start = day_start + timedelta(hours=8)
    tcpa_end = day_start + timedelta(hours=21)

    day_start_timestamp: int = int(day_start.timestamp())

    start_timestamp: int = int(tcpa_start.timestamp())
    end_timestamp: int = int(tcpa_end.timestamp())

    day_len: int = end_timestamp - start_timestamp
    day_mid = int(day_len / 2)

    env = simpy.Environment()
    synthetic_agents = distribute_agents_by_schedule(88, env, day_start_timestamp)

    agents: list[Agent] = synthetic_agents
    synthetic_call = generate_call_data(
        env,
        n_inbound=300,
        n_outbound=500,
        date_start=day_start_timestamp,
        tcpa_start=start_timestamp,
        day_mid=day_mid,
        day_len=day_len,
    )
    calls: list[Call] = synthetic_call

    center = CallCenter(env, agents_list=agents, call_list=calls, day_start=day_start_timestamp, day_end=end_timestamp)

    env.run()
    return center


def main() -> None:
    start_date = "2026-11-06 00:00:00"

    format_pattern = "%Y-%m-%d %H:%M:%S"
    day_start: dt = dt.strptime(start_date, format_pattern)


    for n in range(0,14):
        day = day_start + timedelta(n)
        run = run_sim(day)
        run.get_results()

    
