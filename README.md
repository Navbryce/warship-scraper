# Warship Scraper
Scrapes warship information from Wikipedia. 
Because all the information is user-sourced, most formatting is not consistent Wikipedia-page to page, making the task awkward.
The scraper also calculates various stats about the ships and a similarity score between all the ships.

# Background
I coded this app 5 years ago, while I was in high school.
As a result, the code is not very idiomatic.
Around 2020, it stopped working because the database was deleted and the stack was growing unsupported.
In 2022, I switched to poetry for dependency management, packaged the app in Docker, and allocated a new database on Mongo Atlas, so I could re-deploy it on Heroku.
Any of the changes I made in 2022 were deployment-related (and I didn't change the core of the projectt).

# Stack
- Python (Scraper)
- Poetry
- Node.js and Express (HTTP API)
- MongoDB

# Demo
See the [frontend's repo to access the demo](https://github.com/Navbryce/ABoat)
