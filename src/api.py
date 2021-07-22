from flask import make_response, request
from flask_restful import Resource, Api
from flask_restful.representations.json import output_json
import xml.etree.ElementTree as ET

from drivers import Driver


class InterceptRequestMiddleware:
    """Middleware to manually set request headers.
    The 'mime' var of this class will be used to set the api format (json/xml) instead of the original request headers.
    The problem: this setting takes effect only from the second request (load the page and then reload to switch format),
    even with the use of @before_request decorated function
    """

    mime = 'application/json'

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        """ request cannot be accessed here (outside of request context) like this:
        format = 'xml' if request.args.get('format') == 'xml' else 'json' """
        environ['HTTP_ACCEPT'] = InterceptRequestMiddleware.mime
        return self.wsgi_app(environ, start_response)


class CustomApi(Api):

    @staticmethod
    def output_xml(data, code, headers=None):
        """Make a Flask response with a xml body. Used as a custom representation for API resources"""

        def dict_to_tree_recursive(src_dict: dict, root: ET.Element = None) -> ET.ElementTree:
            """Convert data dict to the Element object (with all children) recursively.
            src_dict (data) is always a dict with a single key at the top level -- this is used as the root tag"""
            if root is None:
                src_top_key = next(iter(src_dict.keys()))
                root = ET.Element(src_top_key)

            for key, value in src_dict.items():
                child = ET.SubElement(root, key)
                if isinstance(value, dict):
                    dict_to_tree_recursive(value, child)
                else:
                    child.text = value
            return root[0]

        tree = dict_to_tree_recursive(data)
        xml_string = ET.tostring(tree, xml_declaration=True, encoding="utf-8")
        resp = make_response(xml_string)
        resp.headers.extend(headers or {})
        return resp

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.representations = {
            'application/json': output_json,
            'application/xml': __class__.output_xml,
        }



class DriversListApi(Resource):
    def get(self):
        drivers_dic = {'drivers': {}}
        for ind, d in enumerate(Driver.all()):
            drivers_dic['drivers'].update({f'driver{ind + 1}': d.driver_info_dictionary()})
        return drivers_dic


class DriverApi(Resource):
    def get(self, name):


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
        InterceptRequestMiddleware.mime = 'application/xml'

        asc_order = True
        report_dic = {'report': {}}
        drivers = Driver.all()
        drivers.sort(key=lambda d: d.best_lap)
        for ind, d in enumerate(drivers):
            report_dic['report'].update({f'place{ind + 1}': d.driver_info_dictionary()})
        return report_dic
