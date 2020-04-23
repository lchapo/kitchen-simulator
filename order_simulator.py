"""Process orders and write to database"""

from datetime import datetime
import json
import simpy

class Kitchen(object):
    """A kitchen has a limited number of cooks to make food in parallel.

    Assume each cook prepares one item at a time, and any cook is capable
    of preparing any item. When an order is received, it goes to an arbitrary
    available cook and takes {cook_time} seconds to prepare. If no cooks
    are available, the order is enqueued until a cook is available.
    """
    def __init__(self, env, num_cooks):
        self.env = env
        self.machine = simpy.Resource(env, num_cooks)

    def prepare_food(self, order_details):
        """The cooking process. Called when a cook is available, and takes {cook_time} to complete"""
        yield self.env.timeout(order_details['cook_time'])


def process_order(env, order_details, kitchen):
    print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - order for {order_details['customer']} received")
    with kitchen.machine.request() as request:
        yield request

        print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - order for {order_details['customer']} is being prepared")
        yield env.process(kitchen.prepare_food(order_details))

        print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - order for {order_details['customer']} finished")


def setup(env, order_details, kitchen):
    """Feed in data"""
    yield env.timeout(order_details['order_time'])
    env.process(process_order(env, order_details, kitchen))


def simulate_orders(speed=1):
    """Simulate orders coming in over time

    Args:
      speed (int): speed at which to run the simulator, where 1 is real
        time, 2 is twice as fast as normal, etc.
    """
    with open('data/orders.json') as f:
        orders = json.load(f)
    # Create an environment and start the setup process
    env = simpy.rt.RealtimeEnvironment(factor=1/speed)
    kitchen = Kitchen(env, num_cooks=2)
    for order_details in orders:
        env.process(setup(env, order_details, kitchen))

    # Execute!
    env.run(until=20)
