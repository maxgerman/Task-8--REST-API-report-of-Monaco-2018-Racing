from flask import make_response, request
from flask_restful import Resource, Api
from flask_restful.representations.json import output_json
import xml.etree.ElementTree as ET

from drivers import Driver


class CustomApi(Api):
    """
    Custom flask_restful Api class for:
        - providing additional representation to accept (xml)
        - output function to convert data (dicts) to xml strings
    """

    @staticmethod
    def output_xml(data, code, headers=None):
        """Make a Flask response with a xml body (output function for xml representation, which we added in __init__)"""

        def dict_to_tree_recursive(src_dict: dict, root: ET.Element = None) -> ET.ElementTree:
            """Convert the data dict to the etree.Element object (including all children) recursively.
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
        request.environ['HTTP_ACCEPT'] = 'application/xml' if request.args.get(
            'format') == 'xml' else 'application/json'

        drivers_dic = {'drivers': {}}
        for ind, d in enumerate(Driver.all()):
            drivers_dic['drivers'].update({f'driver{ind + 1}': d.driver_info_dictionary()})
        return drivers_dic


class DriverApi(Resource):
    def get(self, name):
        request.environ['HTTP_ACCEPT'] = 'application/xml' if request.args.get(
            'format') == 'xml' else 'application/json'

        try:
            d = Driver.get_by_id(name)[0].driver_info_dictionary()
            result_dic = {'driver': d}
        except IndexError:
            return {'error': f'driver \'{name}\' not found'}
        return result_dic


class ReportApi(Resource):
    def get(self):
        request.environ['HTTP_ACCEPT'] = 'application/xml' if request.args.get(
            'format') == 'xml' else 'application/json'

        asc_order = True
        report_dic = {'report': {}}
        drivers = Driver.all()
        drivers.sort(key=lambda d: d.best_lap)
        for ind, d in enumerate(drivers):
            report_dic['report'].update({f'place{ind + 1}': d.driver_info_dictionary()})
        return report_dic
