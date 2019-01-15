from app import app
from marshmallow import Schema, fields, validate, ValidationError
from flask_restful import request


class RequestSchema(Schema):
    pass


def get_arg_types():
    return fields.__all__


class RequestParser():
    def __init__(self):
        self.reqschema = {
            "json": RequestSchema(strict=True),     # content-type: application/json
            "form": RequestSchema(strict=True),     # content-type: multipart/form-data
            "args": RequestSchema(strict=True),     # arguments from url
            "values": RequestSchema(strict=True),   # application/x-www-form-urlencoded,
                                                    # form-data, arguments from url
            "text": RequestSchema(strict=True),     # content-type: text/plain
            "headers": RequestSchema(strict=True),
            "cookies": RequestSchema(strict=True)
            }
        self.help = {}

    def add_argument(self, name, default=None, required=False, type='Str',
                     choices=None, help='', location='values'):
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
                    errs = ', '.join([i + ': ' + ' '.join(err.messages[i]) for i in err.messages])
                    return app.make_response((errs, 422))
        return data
