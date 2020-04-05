CONTAINER="quizmous_api"
ENTRYPOINT="--entrypoint bash"
INTERACTIVE="-it"
NETWORK="db_api"
THIS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
DETACHED=""

hash docker 2>/dev/null && echo "Docker is installed" || (echo "Docker is not installed. Please try again after installing Docker" && exit 1)

echo "Stopping running container if exists"
docker stop ${CONTAINER} postgres_api 2>/dev/null
docker rm ${CONTAINER} postgres_api 2>/dev/null
docker network create ${NETWORK}

echo "Creating postgres container"
docker run -d --name postgres_api --rm --network ${NETWORK} -v ${THIS_DIR}/dummy.sql:/docker-entrypoint-initdb.d/schema.sql -e POSTGRES_USER=api -e POSTGRES_DB=quiz -e POSTGRES_PASSWORD=foobar postgres:12 || (echo "Running postgres container failed. Aborting" && exit 1)

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
        --detach)
            echo "Detaching ${CONTAINER}"
            DETACHED="-d"
            ;;
        --non_interactive)
            echo "Using ${CONTAINER} with non-interactive mode"
            INTERACTIVE=""
            ;;
        --test)
            echo "Using ${CONTAINER} for tests only"
            ENTRYPOINT=""
            docker run ${DETACHED} ${INTERACTIVE} -v ${THIS_DIR}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} --network ${NETWORK} quizmous_api:dev python -m pytest test/*.py test/endtoend/*py --disable-pytest-warnings
            RETVAL=$?
            exit ${RETVAL}
            ;;
        --coverage)
            echo "Using ${CONTAINER} with for coverage"
            ENTRYPOINT=""
            docker run ${DETACHED} ${INTERACTIVE} -v ${THIS_DIR}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} --network ${NETWORK} quizmous_api:dev /bin/bash run_coverage.sh
            exit 0
            ;;
        --*) echo "bad option $1"
            ;;
        *) echo "argument $1"
            ;;
    esac
    shift
done

echo "Running container"
docker run ${DETACHED} ${INTERACTIVE} -v ${THIS_DIR}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} --network ${NETWORK} quizmous_api:dev
echo "Stopped"
if [ $? -ne 0 ]; then
    echo "Using cached version failed. Trying to build the image"
    docker build . -t quizmous_api:dev
    docker run ${DETACHED} ${INTERACTIVE} -v ${THIS_DIR}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} --network ${NETWORK} quizmous_api:dev
fi
