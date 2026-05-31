The files in this directory allow you to spin up a postgres container exactly
like the one in prod. Every ecs/ app will expect this database to exist as it's
where data will be dropped off. So when testing locally, run

`docker compose up -d`

in this directory before testing your ecs apps.

Two things will happen when you do that:
1. The postgres container will start
2. init.sh file will run and recreate the databases/schemas/permissions required 
