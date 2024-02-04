FROM jinaai/jina:3.14.1-py310-standard

RUN apt-get update && apt-get install --no-install-recommends -y git pip nginx && rm -rf /var/lib/apt/lists/*

## install requirements for the gateway
COPY requirements.txt .
RUN pip install --compile -r requirements.txt

# setup the workspace
COPY . /
WORKDIR /workdir


ENTRYPOINT ["lc-serve", "deploy", "main"]