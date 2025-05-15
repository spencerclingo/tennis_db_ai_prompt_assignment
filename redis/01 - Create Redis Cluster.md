The easiest way to get Redis up and running is to use the Redis Cloud. Go to https://redis.com/redis-enterprise-cloud/overview and click on "Try Free" and sign up for a free account. Once you are in, you should be able to create a free database instance of Redis by choosing a Cloud Platform (I chose Google Cloud Platform) and clicking "Let's Start Free". 

If you click on your database in the control panel that should appear after you clicked on "Let's Start Free", you should see the settings for your database. There are many settings but the important ones for now are:

- Public Endpoint: Made up of a url and a port
- Default User
- Default User Password

You will need these values to connect to your now running Redis database.

A good client to connect to your database, view data, configure notifications, and run client commands is RedisInsight available at https://redis.com/redis-enterprise/redis-insight/  

In RedisInsight, you can "Add Redis Database" which will open a settings dialog where you will enter the information for your Redis database. Then you should be able to click on your database and get a connection to it. 

RedisInsight opens up in the Keys view (notice the highlighted key icon on the left). There is a refresh button in the Keys panel. Initially, you won't have any keys to display.

Clicking on the Workbench (looks like a document) icon on the left will take you to a panel where you can enter Redis commands and run them.

To test if everything is up and running, run a ping command

```
ping
```

You should get PONG in response