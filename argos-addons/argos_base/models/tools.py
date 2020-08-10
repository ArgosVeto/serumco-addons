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

def split_consolidated_phones(string_value=False):
    if not string_value:
        return False, False
    phones = string_value.split('##')
    if len(phones) >= 2:
        return phones[0], phones[1]
    return phones[0], False