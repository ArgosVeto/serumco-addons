# -*- encoding: utf-8 -*-

import base64
import requests
import csv
import io
from odoo import fields, _


def str2bool(value=False):
    """
    convert string boolean to boolean
    :param value:
    :return:
    """
    if not value:
        return False
    return value.strip().lower() in ('yes', 'true', 't', '1', 'oui', 'vrai')


def get_image_url_as_base64(url):
    if not url:
        return False
    return base64.b64encode(requests.get(url).content)


def str2none_dict(vals=False):
    """
    This function make a dictionary value to None if value is '' or 'null'
    :param vals:
    :return:
    """
    assert isinstance(vals, dict)
    return dict(map(lambda j: (j[0], str2none(j[1])), vals.items()))


def str2none(value=False):
    """
    :param value:
    :return:
    """
    if (not value or value in ['null']) and isinstance(value, str):
        return None
    return value


def manage_import_report(header=[], lines=[], template=False, errors=[], logger=None):
    """
    This method is used to manage import progression and errors that may occur, used for impex module

    :param header: header of csv file imported
    :param lines: lines imported successfully
    :param template: import template (ir.model.import.template)
    :param errors: errors that occurs during import, contains the tuple row imported (dictionary), errors generated
    :param logger: smile logger
    :return:
    """
    if lines:
        logger.info(_('List of lines imported successfully: %s') % str(lines))
    if errors and template.export_xls and header:
        generate_errors_file(header, template, errors)
        logger.info(
            _('Import finish with errors. Go to History Error Files tab to show the list of stranded lines.'))
        return False
    if errors:
        logger.info(
            _("List of stranded lines: ['%s']") % "', '".join(str(row[0].get('numero'))
                                                             for row in errors if
                                                             row and isinstance(row[0], dict)))
        return False
    if not errors:
        logger.info(_('Import done successfully.'))
    return True


def generate_errors_file(header=False, template=False, data=[]):
    """
    Manage the error file creation containing all the rows that generated errors

    :param header: header of csv file imported
    :param template: import template (ir.model.import.template)
    :param data: errors data to manage
    :return:
    """
    if not data or not template or not header:
        return
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data, delimiter=';')
    csv_writer.writerow(header + ['Errors'])
    for row, error in data:
        csv_writer.writerow([row.get(key) for key in header] + [error])

    content = base64.b64encode(csv_data.getvalue().encode('latin-1'))
    date = str(fields.Datetime.now()).replace(':', '').replace('-', '').replace(' ', '')
    filename = '%s.csv' % (date,)
    create_attachment(template, content, filename)


def create_attachment(template=False, content=None, filename=False):
    """
    Generate attachment in template with the errors file

    :param template: import template (ir.model.import.template)
    :param content: byte format of the file containing errors
    :param filename:
    :return:²
    """
    if not template or not content:
        return False
    model = 'ir.model.import.template'
    if template and hasattr(template, 'attachment_ids'):
        template.attachment_ids = [(0, 0, {'type': 'binary', 'res_model': model,
                                           'res_id': template.id, 'datas': content, 'name': filename})]
    return True