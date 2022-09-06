import numpy as np
from tqdm import tqdm
import enum

class State(enum.Enum):
    free = 1
    finished = 2
    using = 3
class Queue(list):
    def __init__(self):
        super().__init__()

    def push(self, x):
        self.append(x)
    def get(self):
        assert len(self) > 0
        el = self[0]
        return el
    def pop_get(self):
        el = self.get()
        self.pop(0)
        return el
    def isEmpty(self):
        return True if len(self) == 0 else False

class Person:
    def __init__(self, roll_count: int):
        self.roll_count = roll_count
        self.queue_time_vatrushka = 0
        self.queue_time_gorka = 0
        self.roll_count_made = 0
        self.alive = True if self.roll_count else False

        self.inProcess = False

    def roll_down(self):
        assert self.alive
        self.roll_count_made += 1
        if self.roll_count_made == self.roll_count:
            self.alive = False
        self.inProcess = False

    def take_vatrushka(self):
        self.inProcess = True



class Gorka:
    def __init__(self, countdown_time):
        self.countdown_time = countdown_time
        self.countdown = self.countdown_time
        self.usingPerson = None

        self.state = State.free


    def step(self):
        assert not (self.state == State.finished)

        if self.state == State.using:
            assert self.countdown > 0
            self.countdown -= 1

        if self.countdown == 0 and self.state != State.free:
            self.state = State.finished

        return self.state

    def start(self, pers: Person):
        assert self.state == State.free
        self.state = State.using
        self.countdown = self.countdown_time
        self.usingPerson = pers

    def finish(self) -> Person:
        assert self.state == State.finished and self.countdown == 0
        self.state = State.free
        self.usingPerson.roll_down()
        return self.usingPerson


class Simulation:
    def __init__(self, timestamps: int, vatrushka_n_max: int, persons_n: int, strategy: str):
        self.strategy = strategy
        self.timestamps = timestamps
        self.vatrushka_n_max = vatrushka_n_max
        self.vatrushka_n_avaliable = vatrushka_n_max
        self.persons = self.make_persons(persons_n, 1, 10)
        self.time_to_roll_down = 20

        self.GORKA = Gorka(self.time_to_roll_down)

        self.persons_queue = Queue()
        for p in self.persons:
            self.persons_queue.push(p)

        self.roll_down_queue = Queue()

    def make_persons(self, persons_n: int, from_: int, to_: int):
        res = []
        for i in range(persons_n):
            # res.append(Person(np.random.randint(from_, to_)))
            res.append(Person(1))
        return res

    def sim_step(self, t_st):
        gorka_state = self.GORKA.step()

        if gorka_state == State.finished:
            pers = self.GORKA.finish()
            if self.strategy == "ideal":
                if pers.alive:
                    self.persons_queue.push(pers)
                self.vatrushka_n_avaliable += 1
            elif self.strategy == "selfish":
                if pers.alive:
                    self.roll_down_queue.push(pers)
                else:
                    self.vatrushka_n_avaliable += 1
            else:
                raise Exception
        elif gorka_state == State.free and not self.roll_down_queue.isEmpty():
            pers = self.roll_down_queue.pop_get()
            self.GORKA.start(pers)

        while self.vatrushka_n_avaliable > 0:
            if self.persons_queue.isEmpty():
                break

            pers: Person = self.persons_queue.pop_get()
            pers.take_vatrushka()
            self.roll_down_queue.push(pers)
            self.vatrushka_n_avaliable -= 1

        for p in self.roll_down_queue:
            p.queue_time_gorka += 1
        for p in self.persons_queue:
            p.queue_time_vatrushka += 1

    def run(self):
        for t_st in tqdm(range(self.timestamps)):
            self.sim_step(t_st)


if __name__ == '__main__':
    # ideal selfish
    s = Simulation(timestamps=60*60*1600, vatrushka_n_max=1000, persons_n=2000, strategy="selfish")
    s.run()

    res = []
    for i in s.persons:
        res.append((i.queue_time_vatrushka, i.queue_time_gorka, i.roll_count, i.alive))
        print(res[-1])

    s_v = 0
    s_g = 0
    al_count = 0
    for i in res:
        if not i[3]:
            s_v += i[0] / i[2]
            s_g += i[1] / i[2]
            al_count += 1
    s_g /= al_count
    s_v /= al_count

    print("Удовлетворены ", al_count, "из", len(res))
    print(s_v, s_g)
