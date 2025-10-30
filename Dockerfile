FROM python:3.11

RUN pip install "poetry>=2.0.1,<3.0.0"
RUN poetry config virtualenvs.create false

WORKDIR /

# Copy ML package first
COPY ml_package/ ./ml_package/

# Copy backend code
COPY app/ ./app/
COPY poetry.lock ./
COPY pyproject.toml ./
COPY run.py ./
COPY start.sh ./

# Install ML package in editable mode
RUN pip install -e ./ml_package

# Install backend dependencies
RUN poetry install --no-root

EXPOSE 8000

CMD ["sh", "./start.sh"]