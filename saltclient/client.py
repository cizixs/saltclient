#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import requests


class SaltClient(object):
    """Simple salt-api wrapper .

    SaltClient only deals with fundemental salt-api functions, like
    minion list, job status list, module run, get grains.

    Any transaction logic should be wrapped in upper modules.
    """
    TOKEN = None
    EXPIRE_IN = None

    def __init__(self, url, user, password):
        self.url = url.strip('/')
        self.user = user
        self.password = password

    def get_token(self):
        if self.TOKEN and self.EXPIRE_IN > time.time():
            return self.TOKEN

        s = requests.Session()
        s.headers.update({"Accept": "application/json"})
        payload = {
            "username": self.user,
            "password": self.password,
            "eauth": "pam"
        }

        try:
            response = s.post(self.url + "/login", data=payload)
        except requests.ConnectionError:
            raise ValueError("Can't connect to salt-api at {}, "
                             "maybe it's down".format(self.url))

        if response.status_code == 401:
            msg = "Could not authenticate salt-api using provided credentials"
            raise ValueError(msg)

        result = json.loads(response.text)
        if result:
            self.TOKEN = result['return'][0]['token']
            self.EXPIRE_IN = result['return'][0]['expire']
            return self.TOKEN

    def request(self, uri='', method='POST', data=None):
        token = self.get_token()

        s = requests.Session()
        s.headers.update({"Accept": "application/json"})
        s.headers.update({"X-Auth-Token": token})

        try:
            if method == 'POST':
                res = s.post(self.url + uri, data=data)
            elif method == 'GET':
                res = s.get(self.url + uri)
        except requests.ConnectionError:
            raise ValueError("Can't connect to salt-api at {}, "
                             "maybe it's down".format(self.url))

        try:
            return json.loads(res.text)
        except ValueError:
            msg = "Get non-json result from salt-api: %s" % res.text
            raise RuntimeError(msg)

    def _run(self, minion_id, sync, func, arg=tuple()):
        cmd = {
            "client": sync,
            "tgt": minion_id,
            "fun": func
        }

        if arg:
            cmd['arg'] = arg

        return self.request(data=cmd)

    def async_run(self, minion_id, func, arg=tuple()):
        """Run a salt command asynchronically"""
        return self._run(minion_id, 'local_async', func, arg=arg)

    def sync_run(self, minion_id, func, arg=tuple()):
        """Run a salt command synchronically"""
        return self._run(minion_id, 'local', func, arg=arg)

    def _sync_module(self, minion_id):
        """Sync and refresh modules."""

        self._run(minion_id, 'local', 'saltutil.sync_modules')
        self._run(minion_id, 'local', 'saltutil.refresh_modules')

    def jobs(self):
        """Get all jobs result."""
        return self.request('/jobs', method='GET')

    def job(self, jid):
        """Get a job result.

        :params jid: job id, async_run return jid,
                    or use `salt-run jobs.list_jobs` to get it.
        :return job resutl dict.
        """
        return self.request('/jobs/' + jid, method='GET')

    def minion(self, minion_id):
        """Get minion information.

        :params minion_id: minion id used in saltstack system
        :return: a dict containing minion info:
            {'return':[
                {'minion_id' :
                    { 'os': 'Ubuntu', ...}
                }
                ]
            }
            or empty dict: {u'return': [{}]}
        """
        # TODO(wu_wei): add timeout, non-exist minion takes too long
        uri = '/minions/' + minion_id
        res = self.request(uri, method='GET')
        return res['return'][0]

    def grain(self, minion_id, item):
        try:
            res = self.sync_run(minion_id, 'grains.item', arg=item)
            return res['return'][0][minion_id][item]
        except Exception:
            return ''
