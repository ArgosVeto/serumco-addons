# -*- coding: utf-8 -*-


def remove_space(string=''):
	if not string:
		return ''
	if not isinstance(string, str):
		return ''
	return string.replace(' ', '')
