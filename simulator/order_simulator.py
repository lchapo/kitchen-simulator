"""Process orders and write to database"""

from datetime import datetime
import json
import logging
import sys

import simpy

from db.connection import (
    css_cursor,
    execute_sql,
)
from db.migrations.create_orders_table import recreate_orders_table
from parameters.simulation_parameters import (
    NUM_COOKS,
    SIMULATION_SPEED,
)


##########################
##         SETUP        ##
##########################
# configure logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
log.addHandler(
    logging.StreamHandler(sys.stderr)
)

# load data
with open('data/orders.json') as f:
    orders = json.load(f)
with open('data/items.json') as f:
    menu = json.load(f)

# transform items into cook time lookup
cook_times = {i['name']:i['cook_time'] for i in menu}


def get_time(ts):
    """Parse timestamps into epochs; ignore fractional seconds"""
    ts_parts = ts.split('.')
    return int(datetime.strptime(ts_parts[0], '%Y-%m-%dT%H:%M:%S').timestamp())

# seconds before first order to start simulation
TIME_BUFFER = 10
tstamps = [get_time(order['ordered_at']) for order in orders]
ENV_START = min(tstamps) - TIME_BUFFER


##########################
##   MANAGE RESOURCES   ##
##########################
class Kitchen(object):
    """A kitchen has a limited number of cooks to make food in parallel.

    Assume each cook prepares one item at a time, and any cook is capable
    of preparing any item. When an item is received, it goes to an arbitrary
    available cook and takes {cook_time} seconds to prepare. If no cooks
    are available, the item is enqueued until a cook is available.

    Args:
      env (simpy.environment): the simulation environment
      num_cooks (int): total resources available
    """
    def __init__(self, env, num_cooks):
        self.env = env
        self.resources = simpy.Resource(env, num_cooks)
        # track order ids for items started to avoid updating the database
        # as multiple items come in for the same order
        self.orders_started = []

    def prepare_food(self, order_id, cook_time):
        """The cooking process for a single item

        This should be called multiple times per order, once for each
        item within the order.

        Args:
          order_id (int): primary key for the order
          cook_time (int): the seconds for the item to be cooked
        """
        if order_id not in self.orders_started:
            self.orders_started.append(order_id)
            update_db_order_started(self.env, order_id)
        yield self.env.timeout(cook_time)


##########################
##      GENERATORS      ##
##########################
def request_item(env, order, item, kitchen):
    """Request a kitchen resource for one item in an order"""
    with kitchen.resources.request() as request:
        # waiting until a cook is available
        yield request
        # item is being cooked
        yield env.process(kitchen.prepare_food(order['id'], cook_times[item['name']]))
        # item done


def process_order(env, order, kitchen):
    """Process a single order"""
    # wait until {order_time} to trigger order
    yield env.timeout(get_time(order['ordered_at'])-ENV_START)
    if not order['items']:
        log.info(f"Order {order['id']} has no items and will not be processed")
        return
    update_db_order_received(env, order)
    events = []
    for item in order['items']:
        for _ in range(item['quantity']):
            # request each order item simultaneously
            events.append(env.process(request_item(env, order, item, kitchen))) 
    # wait until all items in the order have been cooked
    yield env.all_of(events)
    update_db_order_completed(env, order['id'])


##########################
##      DB UPDATES      ##
##########################
def update_db_order_received(env, order):
    """Inserts an order when it is first received"""
    SQL = f"""
    INSERT INTO orders (id, status, received_at, customer_name, service, total_price, items)
    VALUES (
        {order['id']}
        , 'Queued'
        , {env.now}
        , '{order['name']}'
        , '{order['service']}'
        , {sum([i['price_per_unit'] * i['quantity'] for i in order['items']])}
        , '{json.dumps({i['name'].replace("'", "''"):i['quantity'] for i in order['items']})}'
    );
    """
    with css_cursor() as cur:
        execute_sql(SQL, cur)


def update_db_order_started(env, order_id):
    """Updates the database when the order starts being prepared"""
    SQL = f"""
    UPDATE orders
    SET started_at = {env.now}
    , status = 'In Progress'
    WHERE id = {order_id};
    """
    with css_cursor() as cur:
        execute_sql(SQL, cur)


def update_db_order_completed(env, order_id):
    """Updates the database when the order is completed"""
    SQL = f"""
    UPDATE orders
    SET completed_at = {env.now}
    , status = 'Completed'
    WHERE id = {order_id};
    """
    with css_cursor() as cur:
        execute_sql(SQL, cur)


##########################
##    RUN SIMULATOR     ##
##########################
def simulate_orders(orders, speed=SIMULATION_SPEED, num_cooks=NUM_COOKS):
    """Simulate orders coming in over time

    Args:
      speed (int): speed at which to run the simulator, where 1 is real
        time, 2 is twice as fast, etc.
      num_cooks (int): cooks (simulation resources) available to cook
        items in parallel
    """
    # clear table before starting
    recreate_orders_table()
    # create an environment and start the setup process
    env = simpy.rt.RealtimeEnvironment(
        initial_time=ENV_START,
        factor=1/speed,
        strict=False,
    )
    kitchen = Kitchen(env, num_cooks=num_cooks)
    for idx, order in enumerate(orders):
        order['id'] = idx+1
        env.process(process_order(env, order, kitchen))

    # run simulation
    log.info(f"Starting simulation at speed {speed}X with {num_cooks} cooks")
    env.run()


if __name__ == '__main__':
    simulate_orders(orders)
