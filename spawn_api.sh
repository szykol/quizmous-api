CONTAINER="quizmous_api"
ENTRYPOINT="--entrypoint bash"
INTERACTIVE="-it"
NETWORK="db_api"
hash docker 2>/dev/null && echo "Docker is installed" || (echo "Docker is not installed. Please try again after installing Docker" && exit 1)

echo "Stopping running container if exists"
docker stop ${CONTAINER} postgres_api 2>/dev/null
docker rm ${CONTAINER} postgres_api 2>/dev/null
docker network create ${NETWORK}

echo "Creating postgres container"
docker run -d --name postgres_api --rm --network ${NETWORK} -v ${PWD}/dummy.sql:/docker-entrypoint-initdb.d/schema.sql -e POSTGRES_USER=api -e POSTGRES_DB=quiz -e POSTGRES_PASSWORD=foobar postgres:12 || (echo "Running postgres container failed. Aborting" && exit 1)

while test $# -gt 0
do
    case "$1" in
        --rebuild)
            echo "Rebuilding image"
            docker build . -t quizmous_api:dev
            ;;
        --deamon)
            echo "Using ${CONTAINER} as a deamon"
            ENTRYPOINT=""
            ;;
        --non_interactive)
            echo "Using ${CONTAINER} with non-interactive mode"
            INTERACTIVE=""
            ;;
        --test)
            echo "Using ${CONTAINER} for tests only"
            ENTRYPOINT=""
            docker run ${INTERACTIVE} -v ${PWD}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} --network ${NETWORK} quizmous_api:dev python -m pytest test/*
            RETVAL=$?
            exit ${RETVAL}
            ;;
        --*) echo "bad option $1"
            ;;
        *) echo "argument $1"
            ;;
    esac
    shift
done

docker run ${INTERACTIVE} -v ${PWD}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} --network ${NETWORK} quizmous_api:dev

if [ $? -ne 0 ]; then
    echo "Using cached version failed. Trying to build the image"
    docker build . -t quizmous_api:dev
    docker run -it -v ${PWD}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} --network ${NETWORK} quizmous_api:dev
fi