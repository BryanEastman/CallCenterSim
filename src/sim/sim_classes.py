import simpy
import heapq
from enum import Enum


class AgentState(Enum):
    AVAILABLE = "available"
    BREAK = "break"
    LUNCH = "lunch"
    OFFLINE = "offline"


class CallState(Enum):
    INACTIVE = "inactive"
    QUEUED = "active"
    CANCELED = "canceled"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


class CallCenter:
    def __init__(
        self,
        env: simpy.Environment,
        agents_list: list[Agent],
        call_list: list[Call],
        day_end: int,
    ):
        self.env: simpy.Environment = env
        self.agents_list: list[Agent] = agents_list
        self.call_list: list[Call] = call_list
        self.day_end = day_end

        # manager lists for active and completed calls
        self.available_agents: list[Agent] = []
        self.waiting_call_queue: list[Call] = []
        self.completed_calls: list[Call] = []

        # manager lists for active agents
        self.schedule_processes = [
            env.process(self.process_schedule(a)) for a in self.agents_list
        ]
        self.queue_processes = [
            env.process(self.queue_calls(call=c)) for c in self.call_list
        ]
        self.close_queues_proc = env.process(self.end_day())

    def handle_call(self, call: Call, agent: Agent):
        agent.busy = True
        call.handled_at_time = self.env.now
        print(
            f"call {call.call_id} handled by {agent.agent_id} at {self.env.now} for {call.handle_time} seconds."
        )
        call.state = CallState.COMPLETED

        yield self.env.timeout(call.handle_time)

        self.completed_calls.append(call)
        if agent.state == AgentState.AVAILABLE:
            self.busy = False
            heapq.heappush(self.available_agents, agent)

    def queue_calls(self, call: Call):
        yield self.env.timeout(call.arrival_time - self.env.now)

        call.state = CallState.QUEUED
        heapq.heappush(self.waiting_call_queue, call)

        if isinstance(call, InboundCall):
            self.env.process(self.abandon_after_patience(call))

        print(f"Call Queued: {call.call_id} -> {call.state.value}: {self.env.now}")

        self.dispatch_calls()

    def abandon_after_patience(self, call: InboundCall):
        yield self.env.timeout(call.patience)

        # after waiting, if not handled remove from queue and cancel
        if call.state == CallState.QUEUED:
            call.state = CallState.CANCELED
            call.canceled_at_time = self.env.now

            self.completed_calls.append(call)
            self.waiting_call_queue.remove(call)
            print(
                f"Abandoned Call: {call.call_id} -> {call.state.value}: {self.env.now}"
            )
            heapq.heapify(self.waiting_call_queue)

    def process_schedule(self, agent: Agent):
        for state_name, time in agent.schedule:
            delay = time - self.env.now
            if delay > 0:
                yield self.env.timeout(delay)

            agent.state = state_name
            agent.state_start = self.env.now

            if agent.state == AgentState.AVAILABLE:
                heapq.heappush(self.available_agents, agent)

            if agent.state != AgentState.AVAILABLE:
                try:
                    self.available_agents.remove(agent)
                except ValueError:
                    pass
                else:
                    heapq.heapify(
                        self.available_agents
                    )  # after removing, reset the queue to retain sort

            self.dispatch_calls()
            print(f"{agent.agent_id} -> {agent.state.value}: {self.env.now}")

    def dispatch_calls(self):

        while self.waiting_call_queue and self.available_agents:
            next_call: Call = heapq.heappop(self.waiting_call_queue)
            next_agent: Agent = heapq.heappop(self.available_agents)

            self.env.process(self.handle_call(next_call, next_agent))

    def end_day(self):
        yield self.env.timeout(self.day_end - self.env.now)

        for call in self.waiting_call_queue:
            if not isinstance(call, InboundCall):
                call.state = CallState.TIMEOUT
                call.canceled_at_time = self.env.now
                self.completed_calls.append(call)
                print(
                    f"Call Canceled: {call.call_id} -> {call.state.value}: {self.env.now}"
                )


class Agent(simpy.Resource):
    def __init__(
        self,
        agent_id: str,
        env: simpy.Environment,
        schedule: list[tuple[AgentState, int]],
    ):
        self.agent_id = agent_id
        self.env: simpy.Environment = env
        self._state: AgentState = AgentState.OFFLINE
        self.state_start: float = 0
        self.schedule: list[tuple[AgentState, int]] = schedule
        self.busy: bool = False

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state: AgentState = value
        self.state_start = self.env.now

    def __lt__(self, other):
        return (self.state_start) < (other.state_start)


class Call:
    def __init__(
        self,
        env: simpy.Environment,
        call_id: str,
        arrival_time: int,
        handle_time: int,
        priority: int = -1,
    ):
        self.env = env
        self.call_id = call_id
        self.arrival_time = arrival_time
        self.handle_time = handle_time
        self._state: CallState = CallState.INACTIVE
        self.state_time: int = 0
        self.priority = priority

        # event timestamps
        self.handled_at_time = None
        self.canceled_at_time = None

    def __lt__(self, other):
        return (self.priority, self.arrival_time) < (other.priority, other.arrival_time)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state: CallState = value


class OutboundCall(Call):
    def __init__(
        self, env, call_id: str, arrival_time: int, handle_time: int, priority=1
    ):
        super().__init__(env, call_id, arrival_time, handle_time)
        self.priority = 1


class InboundCall(Call):
    def __init__(
        self, env, call_id: str, arrival_time: int, handle_time: int, patience: int
    ):
        super().__init__(env, call_id, arrival_time, handle_time)
        self.patience: int = patience
        self.priority = 0
