
> - on-chain Point Program [Dashboard](https://app.allora.network?ref=eyJyZWZlcnJlcl9pZCI6IjVlNmEwMjc5LTcxNjEtNDhmYS04NGM3LWEzYzM0MGM4MGIzNyJ9)


#

> - community tasks on [Zealy](https://zealy.io/cw/alloranetwork/invite/IU2cqqMstYG1pEtHTenpn) & [Galxe](https://app.galxe.com/quest/AlloraNetwork)
>

#

<h1 align="center">Price Prediction Worker Node</h1>



## Remove all docker files
```console
# Stop all running containers
docker stop $(docker ps -q)


# Prune everything (containers, images, volumes, networks)
docker system prune -a --volumes -f
```
## Note: Recover your mneomic
```console
allorad keys list
```
keep your keys safe.

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
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
docker version

# Install Docker-Compose
VER=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)

sudo curl -L "https://github.com/docker/compose/releases/download/"$VER"/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose
docker-compose --version

# Docker Permission to user
sudo groupadd docker
sudo usermod -aG docker $USER
```
```console
# Install Go
sudo rm -rf /usr/local/go
sudo curl -L https://go.dev/dl/go1.22.4.linux-amd64.tar.gz | sudo tar -xzf - -C /usr/local
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
# Recover your old wallet with seed-phrase
allorad keys add testkey --recover

#OR

# Create a new wallet
allorad keys add testkey
```

## Get Faucet

> Get uAllo faucet for testnet v2 [here](https://faucet.testnet-1.testnet.allora.network/)



## Install Worker
```console
# Install
cd $HOME && git clone https://github.com/allora-network/basic-coin-prediction-node.git

cd basic-coin-prediction-node


mkdir worker1-data worker2-data worker3-data head-data

# Give certain permissions
sudo chmod -R 777 worker1-data
sudo chmod -R 777 worker2-data
sudo chmod -R 777 worker3-data
sudo chmod -R 777 head-data

# Create head keys
sudo docker run -it --entrypoint=bash -v ./head-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"

# Create worker keys
sudo docker run -it --entrypoint=bash -v ./worker1-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
sudo docker run -it --entrypoint=bash -v ./worker2-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
sudo docker run -it --entrypoint=bash -v ./worker3-data:/data alloranetwork/allora-inference-base:latest -c "mkdir -p /data/keys && (cd /data/keys && allora-keys)"
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
    container_name: inference-basic-eth-pred
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
    container_name: updater-basic-eth-pred
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

  worker1:
    container_name: worker1-basic-eth-pred
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
        allora-node --role=worker --peer-db=/data/peerdb --function-db=/data/function-db \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9011 \
          --boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/'HEAD-ID' \
          --topic=allora-topic-1-worker \
          --allora-chain-key-name=testkey \
          --allora-chain-restore-mnemonic='SEEDPHRASE' \
          --allora-node-rpc-address=https://allora-rpc.testnet-1.testnet.allora.network/ \
          --allora-chain-topic-id=1
    volumes:
      - ./worker1-data:/data
    working_dir: /data
    depends_on:
      - inference
      - head
    networks:
      eth-model-local:
        aliases:
          - worker1
        ipv4_address: 172.22.0.10

  worker2:
    container_name: worker2-basic-eth-pred
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
        allora-node --role=worker --peer-db=/data/peerdb --function-db=/data/function-db \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9012 \
          --boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/'HEAD-ID' \
          --topic=allora-topic-2-worker \
          --allora-chain-key-name=testkey \
          --allora-chain-restore-mnemonic='SEEDPHRASE' \
          --allora-node-rpc-address=https://allora-rpc.testnet-1.testnet.allora.network/ \
          --allora-chain-topic-id=2
    volumes:
      - ./worker2-data:/data
    working_dir: /data
    depends_on:
      - inference
      - head
    networks:
      eth-model-local:
        aliases:
          - worker2
        ipv4_address: 172.22.0.11

  worker3:
    container_name: worker3-basic-eth-pred
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
        allora-node --role=worker --peer-db=/data/peerdb --function-db=/data/function-db \
          --runtime-path=/app/runtime --runtime-cli=bls-runtime --workspace=/data/workspace \
          --private-key=/data/keys/priv.bin --log-level=debug --port=9013 \
          --boot-nodes=/ip4/172.22.0.100/tcp/9010/p2p/'HEAD-ID' \
          --topic=allora-topic-7-worker \
          --allora-chain-key-name=testkey \
          --allora-chain-restore-mnemonic='SEEDPHRADE' \
          --allora-node-rpc-address=https://allora-rpc.testnet-1.testnet.allora.network/ \
          --allora-chain-topic-id=7
    volumes:
      - ./worker3-data:/data
    working_dir: /data
    depends_on:
      - inference
      - head
    networks:
      eth-model-local:
        aliases:
          - worker3
        ipv4_address: 172.22.0.12

  head:
    container_name: head-basic-eth-pred
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
          --private-key=/data/keys/priv.bin --log-level=debug --port=9010 --rest-api=:6000
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

networks:
  eth-model-local:
    driver: bridge
    ipam:
      config:
        - subnet: 172.22.0.0/24

volumes:
  inference-data:
  worker1-data:
  worker2-data:
  worker3-data:
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
Check topic 1 (worker 1):
```console
network_height=$(curl -s -X 'GET' 'https://allora-rpc.testnet-1.testnet.allora.network/abci_info?' -H 'accept: application/json' | jq -r .result.response.last_block_height) && \
curl --location 'http://localhost:6000/api/v1/functions/execute' --header 'Content-Type: application/json' --data '{
    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
    "method": "allora-inference-function.wasm",
    "parameters": null,
    "topic": "1",
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
        "timeout": 10
    }
}' | jq
```

Check topic 2 (worker 2):
```console
network_height=$(curl -s -X 'GET' 'https://allora-rpc.testnet-1.testnet.allora.network/abci_info?' -H 'accept: application/json' | jq -r .result.response.last_block_height) && \
curl --location 'http://localhost:6000/api/v1/functions/execute' --header 'Content-Type: application/json' --data '{
    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
    "method": "allora-inference-function.wasm",
    "parameters": null,
    "topic": "2",
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
        "timeout": 10
    }
}' | jq
```
Check topic 7 (worker 3):
```console
network_height=$(curl -s -X 'GET' 'https://allora-rpc.testnet-1.testnet.allora.network/abci_info?' -H 'accept: application/json' | jq -r .result.response.last_block_height) && \
curl --location 'http://localhost:6000/api/v1/functions/execute' --header 'Content-Type: application/json' --data '{
    "function_id": "bafybeigpiwl3o73zvvl6dxdqu7zqcub5mhg65jiky2xqb4rdhfmikswzqm",
    "method": "allora-inference-function.wasm",
    "parameters": null,
    "topic": "7",
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
        "timeout": 10
    }
}' | jq
```
Response: you will get code: `200` if everything is fine
  
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

### if you got Error 408: when checking topic status
Leave the node connected for atleast 1 to 3 hours. Then you will. find code 200 .Tab tak other nodes ke sath connection establish ho jayega.


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

