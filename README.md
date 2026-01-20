## Start up instructions
1. docker compose down -v

2. docker compose up init-airflow

3. docker compose exec destination_postgres psql -U postgres -d destination_db

Coded this project by following this [tutorial](https://www.youtube.com/watch?v=PHsC_t0j1dU&t=3902s).
