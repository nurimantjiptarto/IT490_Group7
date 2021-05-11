function find_primary() {
    # Goes through all the nodes in POSTGRES_NODES and looks for one that is up
    # and is a PRIMARY
    echo "Looking for a primary node..."
    PRIMARY=""
    for NODE in $POSTGRES_NODES; do
        NODE_IP=$( dig +short $NODE )
        if [ -z $NODE_IP ] || [ $NODE_IP != $MY_IP ]; then
            # https://stackoverflow.com/questions/11231937/bash-ignoring-error-for-a-particular-command
            EXIT_CODE=0
            pg_isready -h $NODE || EXIT_CODE=$?
            if [ $EXIT_CODE -eq 0 ]; then
                echo "$NODE:5432:postgres:postgres:$POSTGRES_PASSWORD" >> ~/.pgpass
                VALUE=$(psql -U postgres -t -h $NODE -d postgres -c "select pg_is_in_recovery()")
                if [ $VALUE == "f" ]; then
                    echo "$NODE is primary node"
                    if [ ! -z $PRIMARY ]; then
                        echo "Two primary nodes detected! Exiting..."
                        exit 1
                    fi
                    PRIMARY=$NODE
                fi
            fi
        fi
    done
}
