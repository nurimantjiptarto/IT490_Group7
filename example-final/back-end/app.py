logging.info("Connecting to the read-only database...")
        postgres_password = os.environ['POSTGRES_PASSWORD']
        conn_r = psycopg2.connect(
            host='db-r',
            database='example',
            user='postgres',
            password=postgres_password
        )

        logging.info("Connecting to the read-write database...")
        postgres_password = os.environ['POSTGRES_PASSWORD']
        conn_rw = psycopg2.connect(
            host='db-rw',
            database='example',
            user='postgres',
            password=postgres_password
        )

def process_request(ch, method, properties, body):
    """
    Gets a request from the queue, acts on it, and returns a response to the
    reply-to queue
    """
    request = json.loads(body)
    if 'action' not in request:
        response = {
            'success': False,
            'message': "Request does not have action"
        }
    else:
        action = request['action']
        if action == 'GETHASH':
            data = request['data']
            email = data['email']
            logging.info(f"GETHASH request for {email} received")
            curr_r.execute('SELECT hash FROM users WHERE email=%s;', (email,))
            row =  curr_r.fetchone()
            if row == None:
                response = {'success': False}
            else:
                response = {'success': True, 'hash': row[0]}
        elif action == 'REGISTER':
            data = request['data']
            email = data['email']
            hashed = data['hash']
            logging.info(f"REGISTER request for {email} received")
            curr_r.execute('SELECT * FROM users WHERE email=%s;', (email,))
            if curr_r.fetchone() != None:
                response = {'success': False, 'message': 'User already exists'}
            else:
                curr_rw.execute('INSERT INTO users VALUES (%s, %s);', (email, hashed))
                conn_rw.commit()
                response = {'success': True}
        else:
            response = {'success': False, 'message': "Unknown action"}
    logging.info(response)
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(response)
    )
