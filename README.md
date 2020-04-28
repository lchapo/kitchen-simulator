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

## Testing
Tests are very easy to run:
```bash
make unittest
```

Tests are run via their own docker-compose file, which in turn uses Dockerfile.test files for each service. This allows us to mount the same volumes and thus create the same filesystem used to run the application, which is import for module imports to work correctly in our test cases. This also allows us to run tests from one place.

# Architecture Overview
The app runs two distinct processes: the order simulator and an analytics dashboard web app. The processes communicate via a shared SQLite database: the order simulator writes to this database and the dashboard reads from it. This separation of concerns allows each process to run with an independent OS, filesystem, and hardware resources such that one could be scaled independently of the other so long as they both communicate via the shared database. The processes are networked via a simple docker-compose file which also mounts a parameters file to each process for convenience in defining all system parameters in one place.

## Order Simulator
The order simulator uses a framework called [SimPy](https://simpy.readthedocs.io/en/latest/) which is helpful in emulating real-time order processing with a fixed number of resources (cooks).

## Dashboard
The dashboard runs inside of a Flask app using an open-source framework called [Dash](https://plotly.com/dash/) which is a high-level framework built on D3 and React. Dash is flexible enough that it would be very easy to extend this dashboard to include custom visualizations, filters, etc.

The data powering the dashboard is re-queried every 5 seconds (by default) using a pre-defined set of SQL Queries, one per chart. The query results are in most cases pulled into a Pandas dataframe which allows for further transformation as necessary and interfaces well with the Dash API.

# Discussion

## Assumptions
* I assumed orders cannot be known in advance, e.g. no part of the system is allowed to have access to the orders.json file data until the order is received in the real time simulation. Processing this data in advance would make analytics much easier, but we would be cheating!
* I assume that all cooks are capable of cooking any food item, and a single order may be split among cooks, and each cook can only cook one item at a time. For example, an order with 3 items may have each of those items cooked in parallel by different cooks. This adds some complexity over having one order solely cooked by one person, but it better mirrors the real world.
* I assumed that the number of cooks is static over time, e.g. there are no bathroom breaks and if our fictional cooks work in shifts, they are hot-swapped in so that the number of total cooks is the same 24 hours a day.
* I assumed that all orders could be converted to PST after doing some quantitative analysis. This assumption allowed me to show time dimensions on the dashboard that are easier for a human to read and categorization of orders by the likely meal being ordered, but there's no guarantee that the PST is the proper local timezone for every order.
* There are a few orders with no items, and I assumed we could simply discard these.
* I assumed that there's no intelligent design behind the order in which items are cooked. Each order is simply added to the queue, which each item in the order processed in the order that it appears in the input data.

## Analytics Use Cases
The dashboard includes a mix of operational metrics and business metrics:
* The top two widgets give insight into order queues: how the queues change over time, and what the current average order time looks like. The top left chart could be used to make staffing decisions to keep the queue manageable during busier hours and prevent overstaffing during quiet hours. The gauge in the top right is more of an immediate, real-time alert for when the queue is bad enough that order completion times become unreasonable.
* The bottom row of the dashboard is focused on higher level insights and KPIs. The stacked bar chart in the bottom left shows how much gross revenue we're bringing in each day, split by service. The pie chart shows an approximate distribution of how much of our revenue comes from different meals, and the bottom middle number is simply a running total of all revenue over the course of the simulation. I focused on revenue rather than order counts because revenue is the best direct reflection of the success of the business. The bottom metrics are not as immediately actionable as the top ones but can provide a better measure of the health of the company and are a starting point for deeper analysis.

In addition, the SQLite database stores historical data for all orders, including customer name, specific menu items ordered, and timestamps for when the order was received, started, and completed. This order metadata allows us to perform a range of analyses: from simple queries like ranking menu items by popularity to more complex analyses like modeling the effects of order completion times on a customer's likelihood of retention.

## Choices & Tradeoffs
* I chose SQLite as a database because it's easy to get started with and fast enough to handle the I/O needed for this simulation. However, I'd recommend a more fully featured database like Postgres for a production workflow.
* I also would not typically recommend using a single database for OLTP and OLAP, especially running concurrently. Again, I love the simplicity of using SQLite as our sole workhorse here, but an evolution of this architecture would involve a sync to a column-oriented database which could be queried by the Flask app without needing to fight for resources used by the database processing orders.
* Running the two distinct processes on separate threads makes it difficult to share state information directly from one to the other, such as the simulation time. While this is possible to implement, it introduces complexity. I opted instead to query the database for the last received timestamp as a proxy for simulation time. It's not precise but is also not central to the analytics dashboard and does not affect any of the metrics shown.
