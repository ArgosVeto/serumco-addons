# -*- encoding: utf-8 -*-


def str2bool(value=False):
    """
    convert string boolean to boolean
    :param value:
    :return:
    """
    if not value:
        return False
    return value.strip().lower() in ('yes', 'true', 't', '1', 'oui', 'vrai')