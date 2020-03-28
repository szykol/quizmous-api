CONTAINER="quizmous_api"
ENTRYPOINT="--entrypoint bash"

hash docker 2>/dev/null && echo "Docker is installed" || (echo "Docker is not installed. Please try again after installing Docker" && exit 1)

echo "Stopping running container if exists"
docker stop ${CONTAINER} 2>/dev/null
docker rm ${CONTAINER} 2>/dev/null

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
        --*) echo "bad option $1"
            ;;
        *) echo "argument $1"
            ;;
    esac
    shift
done

docker run -it -v ${PWD}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} quizmous_api:dev
if [ $? -ne 0 ]; then
    echo "Using cached version failed. Trying to build the image"
    docker build . -t quizmous_api:dev
    docker run -it -v ${PWD}:/usr/local/api -p 8000:8000 --rm --name ${CONTAINER} ${ENTRYPOINT} quizmous_api:dev
fi