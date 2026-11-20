import numpy as np
from sim.sim_classes import Call, InboundCall, OutboundCall
import simpy
from datetime import datetime as dt
from datetime import timedelta


# sample distributions from real calls
def sample_data():  # TODO
    return


# TODO: Better time initialization
def generate_call_data(
    env: simpy.Environment,
    n_inbound: int,
    n_outbound: int,
    date_start: int,
    tcpa_start: int,
    day_mid: float,
    day_len: int,
    seed: int = 42,
) -> list[Call]:
    call_list: list[Call] = []

    rng = np.random.default_rng(seed)

    # TODO: DRY
    
    generated_outbound = [
        OutboundCall(
            env,
            call_id=f"gen_ob_{n}",
            arrival_time=max(1, int(rng.normal(loc=day_mid, scale=day_len / 6)))
            + tcpa_start,
            handle_time=int(rng.gamma(shape=3, scale=70)),
        )
        for n in range(n_outbound)
    ]

    generated_inbound = [
        InboundCall(
            env,
            call_id=f"gen_ib_{n}",
            arrival_time=max(1, int(rng.normal(loc=day_mid, scale=day_len / 4)))
            + date_start,
            handle_time=int(rng.gamma(shape=2, scale=180)),
            patience=int(rng.gamma(shape=1, scale=20)),
        )
        for n in range(n_inbound)
    ]

    call_list += generated_inbound + generated_outbound

    return call_list
