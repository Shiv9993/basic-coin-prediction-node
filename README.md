![666b297b8d80555ff9a25256_allora-points-phase-2](https://github.com/0xmoei/allora-testnet/assets/90371338/6298f73a-3c58-40a6-9d92-725f36456901)

<h1 align="center">Allora Network Point Program</h1>

> - Create a new wallet in Keplr
>
> - Connect to the on-chain Point Program [Dashboard](https://app.allora.network?ref=eyJyZWZlcnJlcl9pZCI6IjVlNmEwMjc5LTcxNjEtNDhmYS04NGM3LWEzYzM0MGM4MGIzNyJ9)


#

> community tasks on [Zealy](https://zealy.io/cw/alloranetwork/invite/IU2cqqMstYG1pEtHTenpn) & [Galxe](https://app.galxe.com/quest/AlloraNetwork)
>

#

<h1 align="center">Price Prediction Worker Node</h1>



## Remove all docker files
```console
# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Remove all images
docker rmi $(docker images -q)

# Remove all volumes
docker volume rm $(docker volume ls -q)

# Remove all networks
docker network rm $(docker network ls -q)

# Prune everything (containers, images, volumes, networks)
docker system prune -a --volumes -f
```
## Note: Recover your mneomic
```console
allorad keys list
```
keep your mnemonic safe.

## Clean all basic-coin-prediction and allora-chain files
```console
cd $HOME
sudo rm -r basic-coin-prediction-node allora-chain
```

## Install dependecies

```console
# Install Packages
sudo apt update & sudo apt upgrade -y

sudo apt install ca-certificates zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev curl git wget make jq build-essential pkg-config lsb-release libssl-dev libreadline-dev libffi-dev gcc screen unzip lz4 -y
```
```console
# Install Python3
sudo apt install python3
python3 --version

sudo apt install python3-pip
pip3 --version
```
```console
# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
docker version

# Install Docker-Compose
VER=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)

curl -L "https://github.com/docker/compose/releases/download/"$VER"/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose
docker-compose --version

# Docker Permission to user
sudo groupadd docker
sudo usermod -aG docker $USER
```
```console
# Install Go
sudo rm -rf /usr/local/go
curl -L https://go.dev/dl/go1.22.4.linux-amd64.tar.gz | sudo tar -xzf - -C /usr/local
echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> $HOME/.bash_profile
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> $HOME/.bash_profile
source .bash_profile
go version
```

## Install Allorad: Wallet
```console
git clone https://github.com/allora-network/allora-chain.git

cd allora-chain && make all

allorad version
```

## Add Wallet
* You can use your keplr seed-phrase to recover your wallet or create a new one
```console
# Recover your wallet with seed-phrase
allorad keys add testkey --recover

#OR

# Create a new wallet
allorad keys add testkey
```

## Get Faucet
> Connect to Allora [dashboard](https://app.allora.network?ref=eyJyZWZlcnJlcl9pZCI6IjVlNmEwMjc5LTcxNjEtNDhmYS04NGM3LWEzYzM0MGM4MGIzNyJ9) to find your Allora address 
> Get uAllo faucet [here](https://faucet.edgenet.allora.network/)



## Install Worker
```console
# Install
cd $HOME && git clone https://github.com/Shiv9993/basic-coin-prediction-node.git

cd basic-coin-prediction-node

mkdir workers
mkdir workers/worker-1 workers/worker-2 workers/worker-3 head-data

# Give certain permissions
sudo chmod -R 777 workers/worker-1
sudo chmod -R 777 workers/worker-2
sudo chmod -R 777 workers/worker-3
sudo chmod -R 777 head-data

# Create head keys
sudo docker run -it --entrypoint=bash -v ./head-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"

# Create worker keys
sudo docker run -it --entrypoint=bash -v ./workers/worker-1:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
sudo docker run -it --entrypoint=bash -v ./workers/worker-2:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
sudo docker run -it --entrypoint=bash -v ./workers/worker-3:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
```
```console
# Copy the head-id
cat head-data/keys/identity
```

## Connect to Allora Chain
* Delete and create new `docker-compose.yml` file
```console
rm -rf docker-compose.yml && nano docker-compose.yml
```

* Copy & Paste the following code in it
* Replace `head-id` & `WALLET_SEED_PHRASE` in worker-1 , worker-2 and worker-3 containers
```console
version: '3'

services:
  inference:
    container_name: inference
    build:
      context: .
    command: python -u /app/app.py
    ports:
      - "8000:8000"
    networks:
      eth-model-local:
        aliases:
          - inference
        ipv4_address: 172.22.0.4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/inference/ETH"]
      interval: 10s
      timeout: 10s
      retries: 12
    volumes:
      - ./inference-data:/app/data

  updater:
    container_name: updater
    build: .
    environment:
      - INFERENCE_API_ADDRESS=http://inference:8000
    command: >
      sh -c "
      while true; do
        python -u /app/update_app.py;
        sleep 24h;
      done
      "
    depends_on:
      inference:
        condition: service_healthy
    networks:
      eth-model-local:
        aliases:
          - updater
        ipv4_address: 172.22.0.5

  head:
    container_name: head
    image: alloranetwork/allora-inference-base-head:latest
    environment:
      - HOME=/data
    entrypoint:
      - "/bin/bash"
      - "-c"
      - |
        if [ ! -f /data/keys/priv.bin ]; then
          echo "Generating new private keys..."
          mkdir -p /data/keys
          cd /data/keys
          allora-keys
        fi
        allora-node --role=head --peer-db=/data/peerdb --function-db=/data/function-db  \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9010 --rest-api=:6000 \
          --boot-nodes=/dns4/head-0-p2p.v2.testnet.allora.network/tcp/32130/p2p/12D3KooWGKY4z2iNkDMERh5ZD8NBoAX6oWzkDnQboBRGFTpoKNDF,/dns4/head-1-p2p.v2.testnet.allora.network/tcp/32131/p2p/12D3KooWQvVHh7m6N3x4ki2RAo2PQSJ8DsHxqfwAUibRGAge1veU,/dns4/head-2-p2p.v2.testnet.allora.network/tcp/32132/p2p/12D3KooWN1c9CVEr1CLVspxWaiBo4u98UqWmYuGRbxyKs9dE3GPf
    ports:
      - "6000:6000"
    volumes:
      - ./head-data:/data
    working_dir: /data
    networks:
      eth-model-local:
        aliases:
          - head
        ipv4_address: 172.22.0.100

  worker-1:
    container_name: worker-1
    environment:
      - INFERENCE_API_ADDRESS=http://inference:8000
      - HOME=/data
    build:
      context: .
      dockerfile: Dockerfile_b7s
    entrypoint:
      - "/bin/bash"
      - "-c"
      - |
        if [ ! -f /data/keys/priv.bin ]; then
          echo "Generating new private keys..."
          mkdir -p /data/keys
          cd /data/keys
          allora-keys
        fi
        # Change boot-nodes below to the key advertised by your head
        allora-node --role=worker --peer-db=/data/peerdb --function-db=/data/function-db \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9011 \
          --boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/head-id \
          --topic=allora-topic-1-worker --allora-chain-worker-mode=worker \
          --allora-chain-restore-mnemonic='SEEDPHRASE' \
          --allora-node-rpc-address=https://allora-rpc.testnet-1.testnet.allora.network/ \
          --allora-chain-key-name=worker-1 \
          --allora-chain-topic-id=1
    volumes:
      - ./workers/worker-1:/data
    working_dir: /data
    depends_on:
      - inference
      - head
    networks:
      eth-model-local:
        aliases:
          - worker1
        ipv4_address: 172.22.0.12

  worker-2:
    container_name: worker-2
    environment:
      - INFERENCE_API_ADDRESS=http://inference:8000
      - HOME=/data
    build:
      context: .
      dockerfile: Dockerfile_b7s
    entrypoint:
      - "/bin/bash"
      - "-c"
      - |
        if [ ! -f /data/keys/priv.bin ]; then
          echo "Generating new private keys..."
          mkdir -p /data/keys
          cd /data/keys
          allora-keys
        fi
        # Change boot-nodes below to the key advertised by your head
        allora-node --role=worker --peer-db=/data/peerdb --function-db=/data/function-db \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9013 \
          --boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/head-id \
          --topic=allora-topic-2-worker --allora-chain-worker-mode=worker \
          --allora-chain-restore-mnemonic='SEEDPHRASE' \
          --allora-node-rpc-address=https://allora-rpc.testnet-1.testnet.allora.network/ \
          --allora-chain-key-name=worker-2 \
          --allora-chain-topic-id=2
    volumes:
      - ./workers/worker-2:/data
    working_dir: /data
    depends_on:
      - inference
      - head
    networks:
      eth-model-local:
        aliases:
          - worker1
        ipv4_address: 172.22.0.13

  worker-3:
    container_name: worker-3
    environment:
      - INFERENCE_API_ADDRESS=http://inference:8000
      - HOME=/data
    build:
      context: .
      dockerfile: Dockerfile_b7s
    entrypoint:
      - "/bin/bash"
      - "-c"
      - |
        if [ ! -f /data/keys/priv.bin ]; then
          echo "Generating new private keys..."
          mkdir -p /data/keys
          cd /data/keys
          allora-keys
        fi
        # Change boot-nodes below to the key advertised by your head
        allora-node --role=worker --peer-db=/data/peerdb --function-db=/data/function-db \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9014 \
          --boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/head-id \
          --topic=allora-topic-7-worker --allora-chain-worker-mode=worker \
          --allora-chain-restore-mnemonic='SEEDPHRASE' \
          --allora-node-rpc-address=https://allora-rpc.testnet-1.testnet.allora.network/ \
          --allora-chain-key-name=worker-3 \
          --allora-chain-topic-id=7
    volumes:
      - ./workers/worker-3:/data
    working_dir: /data
    depends_on:
      - inference
      - head
    networks:
      eth-model-local:
        aliases:
          - worker3
        ipv4_address: 172.22.0.14

networks:
  eth-model-local:
    driver: bridge
    ipam:
      config:
        - subnet: 172.22.0.0/24

volumes:
  inference-data:
  workers:
  head-data:
```
To save: CTRL+X+Y Enter

## Run worker
```console
docker compose up -d --build
```

## Check your node status
### Check running docker containers
```console
# Ensure you are in the right directory
cd $HOME && cd basic-coin-prediction-node

# Check worker 1 logs
docker compose logs -f worker-1

# Check worker 2 logs
docker compose logs -f worker-2

# Check worker 3 logs
docker compose logs -f worker-3
```

### Check Worker node:
Check topic 1:
```console
network_height=$(curl -s -X 'GET' 'https://allora-rpc.testnet-1.testnet.allora.network/abci_info?' -H 'accept: application/json' | jq -r .result.response.last_block_height) && \
curl --location 'http://localhost:6000/api/v1/functions/execute' --header 'Content-Type: application/json' --data '{
    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
    "method": "allora-inference-function.wasm",
    "parameters": null,
    "topic": "allora-topic-1-worker",
    "config": {
        "env_vars": [
            {
                "name": "BLS_REQUEST_PATH",
                "value": "/api"
            },
            {
                "name": "ALLORA_ARG_PARAMS",
                "value": "ETH"
            },
            {
                "name": "ALLORA_BLOCK_HEIGHT_CURRENT",
                "value": "'"${network_height}"'"
            }
        ],
        "number_of_nodes": -1,
        "timeout": 2
    }
}' | jq
```

Check topic 2:
```console
network_height=$(curl -s -X 'GET' 'https://allora-rpc.testnet-1.testnet.allora.network/abci_info?' -H 'accept: application/json' | jq -r .result.response.last_block_height) && \
curl --location 'http://localhost:6000/api/v1/functions/execute' --header 'Content-Type: application/json' --data '{
    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
    "method": "allora-inference-function.wasm",
    "parameters": null,
    "topic": "allora-topic-2-worker",
    "config": {
        "env_vars": [
            {
                "name": "BLS_REQUEST_PATH",
                "value": "/api"
            },
            {
                "name": "ALLORA_ARG_PARAMS",
                "value": "ETH"
            },
            {
                "name": "ALLORA_BLOCK_HEIGHT_CURRENT",
                "value": "'"${network_height}"'"
            }
        ],
        "number_of_nodes": -1,
        "timeout": 2
    }
}' | jq
```
Response: you will get code: `200` if everything is fine
```
{
  "code": "200",
  "request_id": "9660af22-54d0-4219-a1de-3677868b715f",
  "results": [
    {
      "result": {
        "stdout": "Error running script: exit status 1\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWFqPD3xcY37R5kgUePW4ZNgM2ePDv9r96qF68kwFQZ3pU",
        "12D3KooWJiRzp3DFSy6yqspp4KdJSyDkjBdBfq2a1uf2BRBCdAGk",
        "12D3KooWGdo7GZgkcY7stYQbRYoSMuiSeBoUBiLd8JzUcgfDQCMN"
      ],
      "frequency": 21.428571428571427
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3392.0363009974553\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWHRyWdYQhpgrQ2q6CArP8N6UsDXt5mDfML4fybqCFVGEC",
        "12D3KooWPTsR5JMmjtekPzUr9gRdXNit4CMXqDxDHHc2beXcuHyr"
      ],
      "frequency": 14.285714285714286
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3473.133811362153\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWKTidHUzFchp1C38WvVEhBAudBCTxiArbxphgyQi2Qvih"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3426.4731836502633\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWGMAHnaGgoaUz9KiKut9xLEPk66aCW15PLrpotBWS84JM"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3464.5369537965817\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWJcFcL9arJWbwJKyZpZn81J6Tj5fpFW4BG4AvLeGTTSpi"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3366.2086390078493\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWFYAveN1qCyyrrkdUDuueAeA5Dyk7GEZyhYnmxhe5arfT"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3374.8178596710513\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWQMjk6RBAUdsexGoSrGiBRYhEjk6b6QAqiy28uWssJerN"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3455.94009623101\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWQ85FMueZ6rv6XYHK6FbDqKs7wzZP1kkdqvNVSqo3gA1Z"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3383.4270803342533\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWFMUvLousm8qm7RDgxMuA9QhgirsvC24vGNU4wFzgCrTD"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"2925.5640664690764\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWKMWhzRkyBZ4YAUSRGgauHd8yi5DQcfHz3h5zZ9Yktdtz"
      ],
      "frequency": 7.142857142857143
    },
    {
      "result": {
        "stdout": "{\"infererValue\": \"3021.1331\"}\n\n",
        "stderr": "",
        "exit_code": 0
      },
      "peers": [
        "12D3KooWMUaYAnYaFWBjHVTxwgYBdnG5P2doKetE4NzypUjG9Ddm"
      ],
      "frequency": 7.142857142857143
    }
  ],
  "cluster": {
    "peers": [
      "12D3KooWFqPD3xcY37R5kgUePW4ZNgM2ePDv9r96qF68kwFQZ3pU",
      "12D3KooWPTsR5JMmjtekPzUr9gRdXNit4CMXqDxDHHc2beXcuHyr",
      "12D3KooWKMWhzRkyBZ4YAUSRGgauHd8yi5DQcfHz3h5zZ9Yktdtz",
      "12D3KooWJcFcL9arJWbwJKyZpZn81J6Tj5fpFW4BG4AvLeGTTSpi",
      "12D3KooWGdo7GZgkcY7stYQbRYoSMuiSeBoUBiLd8JzUcgfDQCMN",
      "12D3KooWQ85FMueZ6rv6XYHK6FbDqKs7wzZP1kkdqvNVSqo3gA1Z",
      "12D3KooWFMUvLousm8qm7RDgxMuA9QhgirsvC24vGNU4wFzgCrTD",
      "12D3KooWQMjk6RBAUdsexGoSrGiBRYhEjk6b6QAqiy28uWssJerN",
      "12D3KooWHRyWdYQhpgrQ2q6CArP8N6UsDXt5mDfML4fybqCFVGEC",
      "12D3KooWJiRzp3DFSy6yqspp4KdJSyDkjBdBfq2a1uf2BRBCdAGk",
      "12D3KooWFYAveN1qCyyrrkdUDuueAeA5Dyk7GEZyhYnmxhe5arfT",
      "12D3KooWKTidHUzFchp1C38WvVEhBAudBCTxiArbxphgyQi2Qvih",
      "12D3KooWGMAHnaGgoaUz9KiKut9xLEPk66aCW15PLrpotBWS84JM",
      "12D3KooWMUaYAnYaFWBjHVTxwgYBdnG5P2doKetE4NzypUjG9Ddm"
    ]
  }
}
```

### Check Updater node:
```console
curl http://localhost:8000/update
```
Response:
```
0
```

### Check Inference node:
```console
curl http://localhost:8000/inference/ETH
```
Response:
```
{"value":"2564.021586281073"}
```

### Check Docker containers
```console
docker ps
```

### 🚨Error 408: when checking topic status
```console
# Ensure you are in the right directory
cd $HOME && cd basic-coin-prediction-node

# Remove worker container (worker-1 or worker-2)
docker container stop worker-1
docker container rm worker-1

# Restart worker container (worker-1 or worker-2)
docker compose up -d --build
```
