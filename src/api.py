from flask import make_response, request
from flask_restful import Resource, Api, reqparse
from flask_restful.representations.json import output_json
import xml.etree.ElementTree as ET

from drivers import Driver
import utils

parser = reqparse.RequestParser()
parser.add_argument('format')


class CustomApi(Api):
    # FORMAT_MIMETYPE_MAP = {
    #     "json": "application/json",
    #     "xml": "application/xml",
    # }

    @staticmethod
    def output_xml(data, code, headers=None):
        """Make a Flask response with a xml body. Used as a custom representation for API resources"""
        data = '<XML><data>data1</data></XML>'
        resp = make_response(data)
        headers = {'X-my-output-function': 'output_xml'}
        resp.headers.extend(headers or {})
        return resp


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.representations = {
            'application/json': output_json,
            'application/xml': __class__.output_xml,
        }

    def mediatypes(self):
        """Allow all resources to have their representation
        overriden by the `format` URL argument"""

        # format = 'xml' if request.args.get("format") == 'xml' else 'json'
        # mimetype = CustomApi.FORMAT_MIMETYPE_MAP[format]
        # mimetype = 'application/json'
        # print([mimetype] + super().mediatypes())
        return ['application/json']

    def mediatypes_method(self):
        """Return a method that returns a list of mediatypes"""
        return lambda resource_cls: ['application/json'] #+ self.mediatypes() + [self.default_mediatype]


class DriversListApi(Resource):
    def get(self):
        """
        List all the drivers
        It works also with swag_from, schemas and spec_dict
        ---
        parameters:

        responses:
          200:
            description: A single user item
            schema:
              id: User
              properties:
                username:
                  type: string
                  description: The name of the user
                  default: Steven Wilson
         """
        drivers_dic = {'drivers': {}}
        for ind, d in enumerate(Driver.all()):
            drivers_dic['drivers'].update({f'driver{ind+1}': d.driver_info_dictionary()})
        return drivers_dic


class DriverApi(Resource):
    def get(self, name):
        """
        This examples uses FlaskRESTful Resource
        It works also with swag_from, schemas and spec_dict
        ---
        parameters:
          - in: path
            name: name
            type: string
            required: true
        responses:
          200:
            description: A single driver item
            schema:
              id: User
              properties:
                name:
                  type: string
                  description: The name of the user
                  default: Steven Wilson
                team:
                    type: string
                abbr:
                    type: string

         """

        args = parser.parse_args()
        format = 'xml' if args['format'] == 'xml' else 'json'
        if format == 'json':
            try:
                d = Driver.get_by_id(name)[0].driver_info_dictionary()
                result_dic = {'driver': d}
            except IndexError:
                return {'error': f'driver \'{name}\' not found'}
            return result_dic
        else:
            pass




class ReportApi(Resource):
    def get(self):
        asc_order = True
        report_dic = {'report': {}}
        drivers = Driver.all()
        drivers.sort(key=lambda d: d.best_lap)
        for ind, d in enumerate(drivers):
            report_dic['report'].update({f'place{ind+1}': d.driver_info_dictionary()})
        return report_dic


