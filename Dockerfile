FROM python:3.8.13-alpine3.16

WORKDIR /usr/src/app

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

# install gcc
RUN apk update && apk add python3-dev \
                          libc-dev \
                          libffi-dev \
                          libxslt-dev \
                          libxml2-dev \
                          gcc

# Install poetry
RUN pip install "poetry==1.1.13"

# Copy requirements for caching and install
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi
# Add the module to the python path because the code is not present when poetry installs
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/ABoatScraping"

# Install node
RUN apk add nodejs==16.15.0-r1
RUN apk add --update npm

# Copy node dependencies and install
COPY ["./Backend/package.json", "./Backend/package-lock.json*", "./Backend/"]
RUN cd ./Backend && npm install --production

# Copy all the files
COPY . .
WORKDIR /usr/src/app/Backend
CMD ["npm", "start"]