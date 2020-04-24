"""Process orders and write to database"""

from datetime import datetime
import json
import simpy

with open('data/orders.json') as f:
    orders = json.load(f)

# transform items into cook time lookup
with open('data/items.json') as f:
    cook_times = json.load(f)
cook_times = {i['name']:i['cook_time'] for i in menu}

#TODO: write a test case for full and fractional seconds
def get_time(ts):
    """Parse timestamps into epochs; ignore fractional seconds"""
    ts_parts = ts.split('.')
    return int(datetime.strptime(ts_parts[0], '%Y-%m-%dT%H:%M:%S').timestamp())

# seconds before first order to start simulation
TIME_BUFFER = 10
tstamps = [get_time(order['ordered_at']) for order in orders]
start = min(tstamps) - TIME_BUFFER

class Kitchen(object):
    """A kitchen has a limited number of cooks to make food in parallel.

    Assume each cook prepares one item at a time, and any cook is capable
    of preparing any item. When an order is received, it goes to an arbitrary
    available cook and takes {cook_time} seconds to prepare. If no cooks
    are available, the order is enqueued until a cook is available.
    """
    def __init__(self, env, num_cooks):
        self.env = env
        self.resources = simpy.Resource(env, num_cooks)

    def prepare_food(self, cook_time):
        """The cooking process. Called when a cook is available, and takes {cook_time} to complete"""
        yield self.env.timeout(cook_time, value=1)


def request_item(env, order, item, kitchen):
    with kitchen.resources.request() as request:
        # waiting until a cook is available
        yield request
        # item is being cooked
        print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - order {order['id']} item {item['name']} is being cooked")
        # TODO: Commit item in progress to db
        yield env.process(kitchen.prepare_food(menu[item['name']]))
        print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - order {order['id']} item {item['name']} is done")
        # TODO: Commit item done to db


def process_order(env, order, kitchen):
    """Process a single order"""
    # wait until {order_time} to trigger order
    yield env.timeout(get_time(order['ordered_at'])-ENV_START)
    print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - order {order['id']} received")
    # TODO: Commit order received to db
    events = []
    for item in order['items']:
        for _ in range(item['quantity']):
            # request each order item simultaneously
            events.append(env.process(request_item(env, order, item, kitchen))) 
    yield env.all_of(events)
    print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - order {order['id']} completed")


def simulate_orders(orders, speed=1):
    """Simulate orders coming in over time

    Args:
      speed (int): speed at which to run the simulator, where 1 is real
        time, 2 is twice as fast as normal, etc.
    """
    # Create an environment and start the setup process
    env = simpy.rt.RealtimeEnvironment(initial_time=ENV_START, factor=1/speed)
    kitchen = Kitchen(env, num_cooks=20)
    print(f"{env.now} - {datetime.utcnow().strftime('%H:%M:%S')} - starting simulation")
    for idx, order in enumerate(orders):
        order['id'] = idx+1
        env.process(process_order(env, order, kitchen))

    # Execute
    env.run(until=ENV_START+5000)
