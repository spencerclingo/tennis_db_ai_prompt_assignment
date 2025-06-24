# Reliable Systems

## Situation

You have a horizontally scaled data reading and writing system that consists of many nodes arranged in a ring using consistent hashing. You manage load by horizontally scaling, consistent hashing, and a network load balancer.

You find that about once every three months one of the servers might go down or have some issues. This causes huge issues for your customers when this happens. You want to design a system that keeps your system available with zero downtime even when a single server goes down.

## Deliverables

1. Design a system that allows for a nodes to temporarily go down while still giving read and write access to your data with zero downtime. Draw pictures and explain how it works.