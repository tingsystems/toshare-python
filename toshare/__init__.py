#!/usr/bin/python
# coding: utf-8
# (c) 2017 Raul Granados <@pollitux>

import sys
from requests import request

try:
    import json
except ImportError:
    import simplejson as json

__version__ = '0.0.1'
__author__ = 'Raul Granados'

_credentials = ('', '',)
_apiV = 'v1'
_api_base = 'http://api.tosharehq.xyz/api/{}/'.format(_apiV)


class ToShareError(Exception):
    def __init__(self, error_json):
        super(ToShareError, self).__init__(error_json)
        self.error_json = error_json


class MalformedRequestError(ToShareError):
    pass


class AuthenticationError(ToShareError):
    pass


class ProcessingError(ToShareError):
    pass


class ResourceNotFoundError(ToShareError):
    pass


class ParameterValidationError(ToShareError):
    pass


class ApiError(ToShareError):
    pass


class ToShare:
    """
    Build request toshare API
    """

    def __init__(self):
        self.name = None

    _headers = None

    @classmethod
    def auth_api(cls):
        """
        Login in the api
        :return:
        """
        _client_id, _client_secret = _credentials
        payload = {
            'client_id': _client_id, 'client_secret': _client_secret, 'grant_type': 'client_credentials'
        }

        r = request('post', '{}{}'.format(_api_base, 'auth/token'), data=json.dumps(payload))
        if r.status_code != 200:
            raise ToShareError('Authentication error')
        auth = r.json()
        cls._headers = {
            'Authorization': 'Bearer {}'.format(auth['access_token']),
            'content-type': 'application/json',
            'cache-control': 'no-cache',
            'PROJECT-ID': auth['projectId']
        }

    @classmethod
    def build_http_request(cls, method, path, payload=None, params=None):
        cls.auth_api()
        method = str(method).lower()
        body = request(
            method, '{}{}'.format(_api_base, path), json=payload, params=params, headers=cls._headers
        )

        if body.status_code == 200 or body.status_code == 201 or body.status_code == 204:
            response_body = {'status': True}
            try:
                response_body = body.json()
            except Exception:
                pass
            return response_body
        if body.status_code == 400:
            raise MalformedRequestError(body.json())
        elif body.status_code == 401:
            raise AuthenticationError(body.json())
        elif body.status_code == 402:
            raise ProcessingError(body.json())
        elif body.status_code == 404:
            raise ResourceNotFoundError(body.json())
        elif body.status_code == 422:
            raise ParameterValidationError(body.json())
        elif body.status_code == 500:
            raise ApiError(body.json())
        else:
            raise ToShareError(body.json())

    @classmethod
    def to_object(cls, response):
        for key, value in response.items():
            setattr(cls, key, value)
        return cls

    @classmethod
    def create(cls, data):
        """

        :param data: dict with data for create object
        :return: object with data from response
        """
        return cls.to_object(cls.build_http_request('post', cls.__name__, data))

    @classmethod
    def retrieve(cls, oid, params=None):
        """

        :params oid: id of object retrieve
        :return: object with data from response
        """
        return cls.to_object(cls.build_http_request('get', '{}/{}'.format(cls.__name__, oid), params=params))

    @classmethod
    def all(cls, params=None):
        """
        :type params: extra params for build request
        :return: list of objects from response toshare api
        """
        return cls.build_http_request('get', cls.__name__, params=params)

    @classmethod
    def query(cls, params=None):
        """
        :type params: extra params for build request
        :return: list of objects from response toshare api
        """
        return cls.build_http_request('get', cls.__name__, params=params)

    @classmethod
    def update(cls, data, oid):
        """
        :param oid: id object
        :type data: data
        :return: object with data from response
        """
        return cls.to_object(cls.build_http_request('put', '{}/{}'.format(cls.__name__, oid), data))

    @classmethod
    def delete(cls, oid):
        """
        :param oid: id object
        :return: None
        """
        return cls.build_http_request('delete', '{}/{}'.format(cls.__name__, oid))


class Templates(ToShare):
    """
    Opr with Templates of ToShare API
    """

    @classmethod
    def get(cls, slug):
        """
        :params slug: slug of template
        :return: object with data from response
        """
        t = cls.build_http_request('GET', '{}'.format(cls.__name__.lower()), params={'slug': slug})
        if len(t) != 1:
            raise ToShareError('Template not found')
        return cls.to_object(t[0])


class Messages(ToShare):
    """
    Opr with Messages of ToShare API
    """

    @classmethod
    def create(cls, data):
        """
        :param data: dict with data for create object
        :return: object with data from response
        """
        fields_required = ['template', 'data', 'subject', 'fromEmail', 'fromName', 'to']
        for f in fields_required:
            if f not in data:
                raise ToShareError('{} is required'.format(f))
        return cls.to_object(cls.build_http_request('post', cls.__name__.lower(), data))
