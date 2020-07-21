# -*- encoding: utf-8 -*-

import base64
import requests


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