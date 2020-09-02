# -*- encoding: utf-8 -*-

import base64
import requests
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

EXISTING_FORMATS = ['%d/%m/%Y  %H:%M:%S', '%d/%m/%Y  %H:%M']


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


def split_consolidated_phones(string_value=False):
    if not string_value:
        return False, False
    phones = string_value.split('##')
    if len(phones) >= 2:
        return phones[0], phones[1]
    return phones[0], False


def date_from_params(year=False, month=False, day=False):
    if not year or not month or not day:
        return False
    return datetime.datetime(year, month, day).strftime(DEFAULT_SERVER_DATE_FORMAT)


def format_date(date):
    if not date:
        return None
    for format in EXISTING_FORMATS:
        try:
            date = datetime.datetime.strptime(date, format)
        except Exception as e:
            pass
    return date.strftime(DEFAULT_SERVER_DATE_FORMAT) if isinstance(date, datetime.date) else None
