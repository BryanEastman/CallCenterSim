from sim.sim_classes import Agent, AgentState, CallCenter, Call,  OutboundCall as obc, InboundCall as ibc
import simpy

def run_sim() -> None:
    env = simpy.Environment()

    agent_1_schedule: list[tuple] = [
        (AgentState.OFFLINE, 0)
        , (AgentState.AVAILABLE, 10)
        , (AgentState.BREAK, 30)
        , (AgentState.AVAILABLE, 35)
        , (AgentState.LUNCH, 40)
        , (AgentState.AVAILABLE, 45)
        , (AgentState.BREAK, 50)
        , (AgentState.AVAILABLE, 55)
        , (AgentState.OFFLINE, 60)
    ] 
    agent_2_schedule: list[tuple] = [
        (AgentState.OFFLINE, 0)
        , (AgentState.AVAILABLE, 5)
        , (AgentState.BREAK, 6)
        , (AgentState.AVAILABLE, 7)
        , (AgentState.LUNCH, 60)
        , (AgentState.AVAILABLE, 61)
        , (AgentState.BREAK, 62)
        , (AgentState.AVAILABLE, 63)
        , (AgentState.OFFLINE, 64)
    ] 
    agents = [
        Agent("id1", env, agent_1_schedule)
        , Agent("id2", env, agent_2_schedule)
    ]
    calls = [
        obc(env, "ob1", 5, 10)
        , ibc(env, "ib1", 15, 15, 6)
        , ibc(env, "ib2", 31, 15, 2)
    ]

    cs = CallCenter(env, agents, calls, day_end = 70)

    env.run(until=70)
    

def main() -> None:
    run_sim()
