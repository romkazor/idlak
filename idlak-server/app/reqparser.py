# Custom request data parsing to replace flask_restful reqparse
# which was depricated. Should act in a similar manner, although has only
# necessary functionalities

from app import app
from marshmallow import Schema, fields, validate, ValidationError
from flask_restful import request


class RequestSchema(Schema):
    """ A template class for handling request data. Used by RequestParser """
    pass


def get_arg_types():
    """ Returns a list of data types accepted by RequestParser """
    return fields.__all__


class RequestParser():
    """ A class to replace flask request parser,
        contains its most basic methods add_argument and parse_args """

    def __init__(self):
        self.reqschema = {
            # content-type: application/json
            "json": RequestSchema(strict=True),
            # content-type: multipart/form-data
            "form": RequestSchema(strict=True),
            # arguments from url
            "args": RequestSchema(strict=True),
            # application/x-www-form-urlencoded, form-data, arguments from url
            "values": RequestSchema(strict=True),
            # content-type: text/plain
            "text": RequestSchema(strict=True),
            "headers": RequestSchema(strict=True),
            "cookies": RequestSchema(strict=True)
            }
        self.help = {}

    def add_argument(self, name, default=None, required=False, type='Str',
                     choices=None, help='', location='values'):
        """ Adds argument to be parsed from a request

            Args:
                name (str):      name of the argument
                default (obj):   default value (not working yet!)
                required (bool): if True and value is not found, method
                                 parse_args throws errors
                type (str):      type of the argument, for list of arguments
                                 lookup from get_arg_types method
                choices (list):  list of choices if needed, if the value is not
                                 in the list, parse_args throws errors
                help (str):      help message to explain an argument that is
                                 returned with an error if it is thrown
                location (str):  where argument could be found, list of locs:
                                 - json - content-type: application/json
                                 - form - content-type: multipart/form-data
                                 - args - arguments from url
                                 - values - content-type: form-data or
                                            application/x-www-form-urlencoded,
                                            or arguments from url
                                 - text - content-type: text/plain
                                 - headers - request headers
                                 - cookies - request cookies
        """
        if type not in fields.__all__:
            raise ValueError('Argument type {} is invalid'.format(type) +
                             'List of valid types: {}'.format(fields.__all__))
        Type = getattr(fields, type)

        if name is None or name == '':
            raise ValueError('Argument name was not provided!')

        validator = None
        if choices is not None:
            validator = validate.OneOf(choices)

        self.reqschema[location].fields[name] = Type(default=default,
                                                     required=required,
                                                     validate=validator)
        if help != '':
            self.help[name] = help

    def parse_args(self):
        """ Parses request based on arguments provided through add_argument
            method.

            Returns:
                :dict: if the request is correctly processed returns a dict
                       with arguments and their values
                :obj:'flask.wrappers.Response': if the parser failed to process
                                                returns a response object with
                                                an error message
        """
        data = {}
        locations = {
            'json': request.get_json(),
            'form': request.form.to_dict(),
            'args': request.args.to_dict(),
            'values': request.values.to_dict(),
            'text': request.get_data(),
            'headers': dict(zip([i[0] for i in request.headers.to_list()],
                                [i[1] for i in request.headers.to_list()])),
            'cookies': request.cookies
        }
        for loc in locations:
            if len(self.reqschema[loc].fields) > 0:
                try:
                    req = self.reqschema['json'].load(locations[loc])
                    if req.data is not None:
                        data.update(req.data)
                except ValidationError as err:
                    for r in err.messages:
                        if r in self.help:
                            err.messages[r].append(self.help[r])
                    errs = ', '.join([i + ': ' + ' '.join(err.messages[i])
                                      for i in err.messages])
                    return app.make_response((errs, 422))
        return data
