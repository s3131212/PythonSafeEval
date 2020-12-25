if [ ! -d ./.nsjail ]; then
    git clone https://github.com/google/nsjail.git .nsjail
fi
docker build --network=host -t nsjailcontainer .