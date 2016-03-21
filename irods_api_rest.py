from functools import wraps
from bottle import post, get, run, response, request

import os
import subprocess
import json
from tempfile import NamedTemporaryFile
import csv


class IrodsApiRestService(object):

    def __init__(self):
        self.metadata = dict(
            samplesheet=['run', 'fcid', 'read1_cycles', 'read2_cycles', 'index1_cycles', 'index2_cycles', 'is_rapid']
        )
        pass

    def _success(self, body, return_code=200):
        params = request.query
        callback = params.get('callback')
        response.content_type = 'application/json'
        response.status = return_code
        return '{0}({1})'.format(callback, {'result': body})

    def wrap_default(f):
        @wraps(f)
        def wrapper(inst, *args, **kwargs):
            res = f(inst, *args, **kwargs)
            if not res or len(res) == 0:
                return None
            else:

                return inst._success(res)
        return wrapper

    def test_server(self):
        params = request.query
        callback = params.get('callback')
        status = {'status':'Server running'}
        return '{0}({1})'.format(callback, {'result': status })

    @wrap_default
    def get_running_folders(self):
        params = request.query
        cmd = 'get_running_folders'
        res = self._ssh_cmd(user=params.get('user'),
                            host=params.get('host'),
                            cmd=self._get_icmd(cmd=cmd, params=params))

        result = [dict(
            running_folder=str(r)
        ) for r in res['result']]


        return dict(objects=result, success=res.get('success'), error=res.get('error'))

    @wrap_default
    def put_samplesheet(self):
        params = request.query
        samplesheet = json.loads(params.get('samplesheet'))
        f = NamedTemporaryFile(delete=False)

        with  f:
            writer = csv.writer(f)
            writer.writerows(samplesheet)

        local_path = f.name
        dest_path  = os.path.join(params.get('tmp_folder'), os.path.basename(local_path))

        res = self._scp_cmd(user=params.get('user'),
                            host=params.get('host'),
                            local_path=local_path,
                            dest_path=dest_path)

        result = []

        if 'success' in res and res.get('success') in "True":

            params.update(dict(local_path=dest_path,
                               irods_path=os.path.join(params.get('samplesheet_collection'),
                                                       "{}.csv".format(params.get('illumina_run_directory')))))

            res = self._iput(params=params)

            if 'success' in res and res.get('success') in "True":

                for key in self.metadata.get('samplesheet',list()):
                    params.update(dict(attr_name=key,
                                       attr_value=str(params.get(key,''))))

                    res = self._iset_attr(params=params)


                result = res.get('result')

        f.close()
        if os.path.exists(local_path):
            os.remove(local_path)

        return dict(objects=result, success=res.get('success'), error=res.get('error'))

    def _iput(self, params):
        cmd = 'iput'
        res = self._ssh_cmd(user=params.get('user'),
                            host=params.get('host'),
                            cmd=self._get_icmd(cmd=cmd, params=params))

        return res

    def _iset_attr(self, params):
        cmd = 'iset_attr'
        res = self._ssh_cmd(user=params.get('user'),
                            host=params.get('host'),
                            cmd=self._get_icmd(cmd=cmd, params=params))

        return res



    def _scp_cmd(self, user, host, local_path, dest_path):
        remote = "{}@{}:{}".format(user, host, dest_path)
        ssh = subprocess.Popen(["scp", local_path, remote],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        result = [line.rstrip('\n') for line in ssh.stdout.readlines()]
        error = ssh.stderr.readlines()

        if error:
            result = dict(success='False', error=error,  result=[])
        else:
            result = dict(success='True',  error=[], result=result)

        return result

    def _ssh_cmd(self, user, host, cmd):
        remote = "{}@{}".format(user, host)
        ssh = subprocess.Popen(["ssh", remote, cmd],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        result = [line.rstrip('\n') for line in ssh.stdout.readlines()]
        error = ssh.stderr.readlines()

        if error:
            result = dict(success='False', error=error,  result=[])
        else:
            result = dict(success='True',  error=[], result=result)

        return result

    def _get_icmd(self, cmd, params):

        icmds = dict(
            get_running_folders="ls {} | grep XX".format(params.get('run_folder')),

            iput="iput -R {} {} {}".format(params.get('irods_resource'),
                                           params.get('local_path'),
                                           params.get('irods_path')),

            iset_attr="imeta set -d {} {} {}".format(params.get('irods_path'),
                                                      params.get('attr_name'),
                                                      params.get('attr_value'))
        )

        return icmds.get(cmd)


