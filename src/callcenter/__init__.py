from sim.sim_classes import *
from sim.generate_calls import *
from sim.generate_agents import *
import polars as pl

import simpy

# TODO: remove these placeholders
format_pattern = "%Y-%m-%d %H:%M:%S"
day_start = dt.strptime("2026-11-06 00:00:00", format_pattern)
day_end = day_start + timedelta(days=1)

start_timestamp: int = int(day_start.timestamp())
end_timestamp: int = int(day_end.timestamp())

day_len: int = end_timestamp - start_timestamp
day_mid = int(day_len / 2)


def run_sim() -> CallCenter:
    env = simpy.Environment()
    synthetic_agents = distribute_agents_by_schedule(64, env)

    agents: list[Agent] = synthetic_agents
    seed = 4
    synthetic_call = generate_call_data(env, 50, 600, day_mid=day_mid, day_len=day_len)
    calls: list[Call] = synthetic_call

    center = CallCenter(env, agents, calls, day_end=end_timestamp)

    env.run()
    return center


def main() -> None:
    run = run_sim()

    res = run.get_results()

    df = pl.DataFrame(res, schema = ["Call ID", "Arrival Time", "Handled Time", "Canceled Time", "Completed Time", "Call State"], orient="row")
    summary_df = df.with_columns(
        (pl.coalesce(pl.col("Handled Time"), pl.col("Canceled Time")) - pl.col("Arrival Time")).alias("Wait Seconds"),
        (pl.col("Completed Time") - pl.col("Handled Time")).alias("Handle Seconds"),
        pl.from_epoch(pl.col(["Arrival Time", "Handled Time", "Canceled Time", "Completed Time"]), time_unit="s")
    )
    print(summary_df.head())
    print(summary_df.select("Wait Seconds", "Handle Seconds").describe())
