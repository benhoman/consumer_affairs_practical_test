# Consumer Affairs Practical Test - The Eye

## Summary
This was a fun little project, at the end of this writeup I'll be just over two hours. The time constraints definitely forced me to go in a specific direction. Ideally I would've had the time to have written tests and organized this on disk a lot better but I chose to spend the time putting some actual functionality together.

## Entities
I created two different models to store event and user session information. While there was no specific guidance around the Session model other than it needed an id, I assumed that this could potentially grow into a larger object so I wanted to create that separate model to be able to easily interate. Events are connected to a UserSession via a session_id foreign key. In the interest of simplicity to get something working quickly in SQLite I did not implement the session_id as a uuid but as a simple string, this is something I would change depending on the database that was used.
I added some very basic static validation for different types of events just based on the keys that were in the json examples. I'm not really happy with where the solution I implemented is currently at but I think it would be easily expandable.
An event POST will try to create a new UserSession record based on the session_id that was submitted; I'm currently relying on the database to throw an integrity error so avoid duplicate UserSession record and watching for that exception.
I assumed given the time constraint that the applications being recognized as "trusted clients" to "The Eye" just meant that authentication wasn't required yet.

## Constraints & Requirements
All requests send some sort of response. The create event functionality returns a 204 No Content response so that I could process the event creation as a background task. Next steps here would be to implement a more robust solution to this such as celery workers and allow easier monitoring of tasks.
Models both have primary keys. The Event model is currently using an autoincrementing primary key but additional constraints could be added if additional uniqueness was required.
The project was created using FastAPI. In my initial interview Waldecir brought up FastAPI so I thought this was a great opportunity to work with that a bit, it's also really great for getting up and running quickly which was important here.

## Use cases
I added routes to query by session or category. Timestamp are stored as actual timestamp values so querying by time range could be implemented fairly easily.
The foundation is in place to build in error monitoring. The two example issues are being handled currently.

## Pluses
I dockerized the application as simply as possible due to time constraints. If this was something I had some more time to prototype I would make the app docker image a little more production ready. Additionally, I would build out the environment to mimic the production stack as closely as possible in the docker-compose file.
I cheated a little here but FastAPI provides some nice documentation that I included.
