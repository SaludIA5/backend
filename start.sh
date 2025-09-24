#!/bin/sh

echo "Current directory: $(pwd)"
echo "Running migrations..."

poetry run alembic -c app/alembic.ini upgrade head

# echo "Running seeds..."
# export PYTHONPATH="/backend:$PYTHONPATH"
# for seed in app/databases/postgresql/seeds/*.py; do
#     if [ -f "$seed" ]; then
        
#         case "$seed" in
#             *__init__.py) continue ;;
#         esac
#         echo "Executing $seed..."
#         poetry run python "$seed"
#     fi
# done

echo "Starting FastAPI application..."
poetry run python run.py