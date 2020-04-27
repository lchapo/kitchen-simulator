# Overview
This repo simulates the real-time processing of food orders received by one kitchen. An order may have multiple items, and the kitchen has a fixed number of cooks who can cook one item at a time. If no cooks are available, the items are added to a queue and processed in order as soon as a cook becomes free. The simulator may be run at multiples of real time to speed things up.

As the simulator runs, it stores order data in a local SQLite database that is shared with a Flask app running on a separate thread. The Flask app displays a data dashboard giving real-time insight into operational and business metrics while the simulation is running.

The analytics dashboard looks like this:
![dashboard](./images/dashboard.png)

# Run the Simulation Locally
## Requirements
Docker and the docker-compose CLI need to be installed on your machine. For best results, increase your Docker Desktop resources above their default levels.

## How to Run
1) From the top level directory, run the following:
```bash
docker-compose up --build
```
2) Open a web browser to [localhost:8050](http://localhost:8050/)
3) (Optional) Change the parameters in [parameters/simulation_parameters.py](./parameters/simulation_parameters.py) and re-run steps 1 and 2 to see how the simulation changes

# Architecture Overview



# Discussion

## Assumptions
- Assumed orders are not known in advance, e.g. no part of the system is allowed to have access to the orders.json file data until the order is received in the real time simulation. Processing this data in advance would make analytics much easier, but we would be cheating!
- Assume that all cooks are capable of cooking any food item, and a single order may be split among cooks, and each cook can only cook one item at a time. For example, an order with 3 items may have each of those items cooked in parallel by different cooks. This adds some complexity over having one order solely cooked by one person, but it better mirrors the real world.
- Assume the number of cooks is static over time, e.g. there are no bathroom breaks and if our fictional cooks work in shifts, they are hot-swapped in so that the number of total cooks is the same 24 hours a day.
- Assumed all orders were in PST after doing some quantitative analysis.
- There are a few orders with no items. Assume we can simply discard these.
- Assume there's no thought process behind which items are cooked first from an order.

## Use Cases

## Choices & Tradeoffs

