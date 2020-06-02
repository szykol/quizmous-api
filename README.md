# quizmous-api

Api for quizmous web app

## Prerequisties

You need to have docker to build the app

General code documentation can be found [here](https://szykol.github.io/quizmous-api/).

API docs generated using swagger can be found [here](https://szykol.github.io/quizmous-api/api.html).

## Quick start

For unix users:

```
./setup_api.sh --rebuild --deamon

curl localhost:8000 # to see if it works

./setup_api.sh # launches the docker container with bash entrypoint
./setup_api.sh --test # launches tests
```

## Endpoints

```
/ [GET]
```

returns

```
{"name": "quizmous", "version": "0.0.1"}
```

### This project uses github actions to perform builds and running tests on every commit
