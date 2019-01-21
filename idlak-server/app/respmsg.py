from app import db
from flask import jsonify
from flask.json import dumps


def mk_response(*argv):
    """ Sends a response message based on arguments

        Args:
            - If one argument is provided and it is a string, it is sent as a
              message. If it is not a string it is sent as it is.
            - If two arguments are provided it is assumed that the first
              should act as a message and the second as response status code.
              Therefore, if first argument does not come in string format,
              it is converted into such.
            - If more than two arguments are provided it is assumed that the
              last should act as a status code and the rest should be included
              in the message. Therefore, they are converted into string format
              if they do not come in such and sent as a list of messages.

        Returns:
            :obj:'Response': a response object that contains the appropriate
                             message and status code (in consistent format)
    """
    if len(argv) == 1:
        if isinstance(argv[0], str):
            msg = argv[0]
            code = 200
            response = db.app.make_response((dumps({"message": msg}), code))
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return args[0]
    elif len(argv) == 2:
        if isinstance(argv[0], str) and isinstance(argv[1], int):
            msg = argv[0]
            code = argv[1]
        elif isinstance(argv[0], list) and isinstance(argv[1], int):
            msg = ', '.join(argv[0])
            code = argv[1]
        elif isinstance(argv[0], dict) and isinstance(argv[1], int):
            msg = ', '.join([i + ': ' + str(argv[0][i]) for i in argv[0]])
            code = argv[1]
        else:
            msg = str(argv[0])
            code = argv[1]

        response = db.app.make_response((dumps({"message": msg}), code))
        response.headers['Content-Type'] = 'application/json'

        return response
    else:
        code = argv[-1]
        msg = []
        for i in argv[:-1]:
            if isinstance(i, str):
                msg.append(i)
            elif isinstance(i, list):
                msg.append(', '.join(i))
            elif isinstance(argv[0], dict):
                msg.append(', '.join([j + ': ' + str(i[j]) for j in i]))
            else:
                msg.append(str(i))
        response = db.app.make_response((dumps({"message": msg}), code))
        response.headers['Content-Type'] = 'application/json'
        return response
