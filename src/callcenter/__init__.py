from sim.sim_classes import *
from sim.generate_calls import *
from sim.generate_agents import *
import polars as pl
import itertools
from pathlib import Path
import os

import simpy

export_root = Path(str(os.getenv("EXPORT_ROOT")))


def run_sim(day_start) -> CallCenter:

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
        300,
        500,
        date_start=day_start_timestamp,
        tcpa_start = start_timestamp,
        day_mid=day_mid,
        day_len=day_len,
    )
    calls: list[Call] = synthetic_call

    center = CallCenter(env, agents, calls, day_end=end_timestamp)

    env.run()
    return center


def main() -> None:
    start_date = "2026-11-06 00:00:00"

    format_pattern = "%Y-%m-%d %H:%M:%S"
    day_start = dt.strptime(start_date, format_pattern)

    days = [day_start + timedelta(days=n) for n in range(0, 14)]
    runs = [run_sim(day) for day in days]

    res = [run.get_results() for run in runs]

    all_results = list(itertools.chain.from_iterable(res))

    df = pl.DataFrame(
        all_results,
        schema=[
            "Call ID",
            "Arrival Time",
            "Handled Time",
            "Canceled Time",
            "Completed Time",
            "Call State",
            "Call Direction",
        ],
        orient="row",
        infer_schema_length=len(all_results),
    )
    summary_df = (
        df.with_columns(
            (
                pl.coalesce(pl.col("Handled Time"), pl.col("Canceled Time"))
                - pl.col("Arrival Time")
            ).alias("Wait Seconds"),
            (pl.col("Completed Time") - pl.col("Handled Time")).alias("Handle Seconds"),
            pl.from_epoch(
                pl.col(
                    ["Arrival Time", "Handled Time", "Canceled Time", "Completed Time"]
                ),
                time_unit="s",
            )
            .dt.replace_time_zone("UTC")
            .dt.convert_time_zone("America/Chicago"),
        )
        .with_columns(
            arrival_hour=pl.col("Arrival Time").dt.hour(),
            abandoned=pl.when(pl.col("Call State") == "canceled").then(1).otherwise(0),
        )
        .rename({"Call ID": "CallID"})
    )
    print(summary_df.head())
    print(summary_df.select("Wait Seconds", "Handle Seconds").describe())
    print(
        summary_df.group_by(["arrival_hour", "Call Direction"])
        .agg(
            pl.col("abandoned").sum().alias("sum"),
            pl.col("abandoned").mean().alias("mean"),
            pl.col("abandoned").len().alias("count"),
        )
        .pivot(
            index="arrival_hour", on="Call Direction", values=["sum", "mean", "count"]
        )
        .sort("arrival_hour")
    )
    summary_df.write_csv(export_root / "call_logs" / "call_logs.out.csv")
