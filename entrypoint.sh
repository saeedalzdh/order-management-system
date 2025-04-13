#!/bin/sh

# If .env exists, load the environment variables
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  set -a
  . .env
  set +a
fi

# Wait for PostgreSQL to be ready
until nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for postgres..."
  sleep 2
done

echo "Database up and running..."

# Run the application
exec "$@"