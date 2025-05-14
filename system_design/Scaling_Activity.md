# Scaling

## Learning Goals
- Gain a working understanding of scaling up versus scaling out.
- Understand cloud computing costs

## Situation
You have a growing successful company that sells books online. You are using a single server that hosts an in-memory database of 128 Gb. It has 32 cores and is able to successfully respond to 200,000 requests per second and only costs $1.25 per hour. However, your customer base is growing and you are getting issues where at peek load times people are getting errors as the single server just cannot process requests fast enough. 

There are no available hardware options to scale up, you already have the best and fastest server available. 

You are asked to design a "scale-out" solution using cloud 1-core VMs that each can take about 5000 requests per second and have 2Gb memory and only cost $.02 per hour each. Your friend says you can use his network load balancer system (for free) which has a capability of distributing requests to a random server in your group of servers.

## Deliverables
1. Design a system using smaller VMs and a load balancer to replace the single large server. Draw a picture and explain how it works.

2. Compare costs between the two systems per hour.

3. Describe costs and needed VMs to handle 200,000 requests per second (RPS) in your distributed system.

4. Describe costs and needed VMs to handle 10,000,000 requests per second (RPS) in your distributed system.

