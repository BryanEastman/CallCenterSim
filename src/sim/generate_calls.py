from tracemalloc import start
import numpy as np
from sim.sim_classes import Call, InboundCall, OutboundCall
import simpy
from datetime import datetime as dt, timedelta

format_pattern = "%Y-%m-%d %H:%M:%S"
day_start = dt.strptime("2026-11-06 00:00:00", format_pattern)
day_end = day_start + timedelta(days=1)

start_timestamp = day_start.timestamp()
end_timestamp = day_end.timestamp()


day_len = end_timestamp - start_timestamp
day_mid = int(day_len / 2)


# sample distributions from real calls
def sample_data():  # TODO
    return


# helper class for batch call generations
def generate_call_data(
    env: simpy.Environment,
    n_inbound: int,
    n_outbound: int,
    day_mid: float,
    day_len: int,
    seed: int = 42,
) -> list[Call]:  # TODO
    call_list: list[Call] = []

    rng = np.random.default_rng(seed)

    generated_outbound = [
        OutboundCall(
            env,
            call_id=f"gen_ob_{n}",
            arrival_time=max(1, int(rng.normal(loc=day_mid, scale=day_len / 6))),
            handle_time=int(rng.gamma(shape=3, scale=70)),
        )
        for n in range(n_outbound)
    ]

    generated_inbound = [
        InboundCall(
            env,
            call_id=f"gen_ib_{n}",
            arrival_time=max(1,int(rng.normal(loc=day_mid, scale=day_len / 6))),
            handle_time=int(rng.gamma(shape=2, scale=180)),
            patience=int(rng.gamma(shape=1, scale=20)),
        )
        for n in range(n_inbound)
    ]

    call_list += generated_inbound + generated_outbound

    return call_list
