
from functools import wraps
from bottle import post, get, run, response, request

import xml.etree.ElementTree as ET
import os
import subprocess
import json
from tempfile import NamedTemporaryFile
import csv
import uuid
from alta.objectstore import build_object_store


class IrodsApiRestService(object):
    def __init__(self):
        self.metadata = dict(
            rundir_collection=[
                'run',
                'fcid',
                'read1_cycles',
                'read2_cycles',
                'index1_cycles',
                'index2_cycles',
                'is_rapid',
                'date',
                'scanner_id',
                'scanner_nickname',
                'pe_kit',
                'sbs_kit',
                'index_kit',
                'pe_id',
                'sbs_id',
                'index_id',
            ]
        )
        pass

    def _success(self, body, return_code=200):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        response.content_type = 'application/json'
        response.status = return_code
        return json.dumps({'result': body}, encoding='latin1')

    def _get_params(self, request_data):
        for item in request_data:
            return eval(item)

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
        params = self._get_params(request.forms)
        callback = params.get('callback')
        status = {'status': 'Server running'}
        return '{0}({1})'.format(callback, {'result': status})

    @wrap_default
    def get_running_folders(self):
        params = self._get_params(request.forms)
        cmd = 'get_running_folders'
        result = list()
        for this_run_folder in params.get('run_folders'):
                params.update(dict(run_folder=this_run_folder))
                params.update(dict(run_xml_file='dummy'))
                res = self._ssh_cmd(user=params.get('user'),
                                    host=params.get('host'),
                                    cmd=self._get_icmd(cmd=cmd, params=params))

                result.extend([dict(
                    path=str(this_run_folder),
                    running_folder=str(r),
                    run_info=self._get_run_info(params=params,
                                                run=str(r)),
                    run_parameters=self._get_run_parameters(params=params,
                                                            run=str(r)),
                ) for r in res['result']])

        result.append(dict(
            running_folder='MISSING RUN FOLDER',
            run_info=dict()))

        return dict(objects=result, success=res.get('success'), error=res.get('error'))

    @wrap_default
    def put_samplesheet(self):

        params = self._get_params(request.forms)

        # creating samplesheet file
        samplesheet = json.loads(params.get('samplesheet'))
        f = NamedTemporaryFile(delete=False)

        with f:
            writer = csv.writer(f)
            writer.writerows(samplesheet)

        local_path = f.name

        # creating run_dir collection
        rundir_collection = os.path.join(params.get('samplesheet_collection'),params.get('illumina_run_directory'))
        params.update(dict(collection=rundir_collection))

        res = self._imkdir(params)

        if 'success' in res and res.get('success') in "True":

            params.update(dict(local_path=local_path,
                               irods_path=os.path.join(rundir_collection, "SampleSheet.csv")))

            res = self._iput(params=params)

            if 'success' in res and res.get('success') in "True":
                for key in self.metadata.get('rundir_collection', list()):
                    params.update(dict(attr_name=key,
                                       attr_value=str(params.get(key, '')),
                                       irods_path=rundir_collection)
                                  )

                    self._iset_attr(params=params)
        f.close()
        if os.path.exists(local_path):
            os.remove(local_path)

        return dict(objects=res.get('result'), success=res.get('success'), error=res.get('error'))

    def _get_irods_conf(self, params):
        return dict(host=params.get('irods_host'),
                    port=params.get('irods_port'),
                    user=params.get('irods_user'),
                    password=params.get('irods_password').encode('ascii'),
                    zone=params.get('irods_zone'))

    def _iinit(self, params):
        ir_conf = self._get_irods_conf(params)
        ir = build_object_store(store='irods',
                                host=ir_conf['host'],
                                port=ir_conf['port'],
                                user=ir_conf['user'],
                                password=ir_conf['password'].encode('ascii'),
                                zone=ir_conf['zone'])
        return ir

    def _imkdir(self, params):
        try:
            ir = self._iinit(params)
            collection = ir.create_object(dest_path=params.get('collection'), collection=True)

            if collection and collection.path and len(collection.path)>0:
                res = dict(success='True', error=[], result=dict(name=collection.name, path=collection.path))
            else:
                res = dict(success='False', error=[], result=[])
        except:
            res = dict(success='False', error=[], result=[])

        return res

    def _iput(self, params):
        try:
            ir = self._iinit(params)
            ir.put_object(source_path=params.get('local_path'), dest_path=params.get('irods_path'))
            obj = ir.get_object(params.get('irods_path'))

            if obj and obj.path and len(obj.path) > 0:
                res = dict(success='True', error=[], result=dict(name=obj.name, path=obj.path))
            else:
                res = dict(success='False', error=[], result=[])
        except:
            res = dict(success='False', error=[], result=[])

        return res

    def _iset_attr(self, params):
        try:
            ir = self._iinit(params)
            if params.get('attr_name') and len(params.get('attr_name')) > 0:

                ir.add_object_metadata(path=params.get('irods_path'),
                                       meta=(params.get('attr_name'),
                                             params.get('attr_value') if len(params.get('attr_value')) > 0 else None))
        except:
            pass

    def _get_run_info(self, params, run):

        def _run_info_parser(run_info):
            result = dict()
            if len(run_info['result']) > 0:
                root = ET.fromstringlist(run_info['result'])
                result = dict(
                    reads=[r.attrib for r in root.iter('Read')],
                    fc_layout=[fc.attrib for fc in root.iter('FlowcellLayout')],
                )
            return result

        cmd = 'get_run_info'
        params.update(dict(this_run=run))
        res = self._ssh_cmd(user=params.get('user'),
                            host=params.get('host'),
                            cmd=self._get_icmd(cmd=cmd, params=params))

        return _run_info_parser(res)

    def _get_run_parameters(self, params, run):

        def _run_parameters_parser(run_parameters):
            result = dict()
            if len(run_parameters['result']) > 0:
                root = ET.fromstringlist(run_parameters['result'])
                result = dict(
                    run_info=dict(
                        run_id=list(root.iter('RunID')).pop(0).text if len(list(root.iter('RunID'))) else '',
                        fc_id=list(root.iter('Barcode')).pop(0).text if len(list(root.iter('Barcode'))) else '',
                        date=list(root.iter('RunStartDate')).pop(0).text if len(
                            list(root.iter('RunStartDate'))) else '',
                        scanner_id=list(root.iter('ScannerID')).pop(0).text if len(
                            list(root.iter('ScannerID'))) else '',
                        scanner_number=list(root.iter('ScannerNumber')).pop(0).text if len(
                            list(root.iter('ScannerNumber'))) else '',
                    ),

                    reads=[r.attrib for r in root.iter('Read')],
                    reagents=dict(
                        sbs=dict(
                            kit=list(root.iter('Sbs')).pop(0).text if len(list(root.iter('Sbs'))) else '',
                            id=list(root.iter('SbsReagentKit')).pop(0).find('ID').text if len(
                                list(root.iter('SbsReagentKit'))) else '',
                        ),
                        index=dict(
                            kit=list(root.iter('Index')).pop(0).text if len(list(root.iter('Index'))) else '',
                            id=list(r.find('ReagentKit').find('ID').text for r in root.iter('Index') if
                                    r.find('ReagentKit') is not None).pop() if len(list(
                                r.find('ReagentKit').find('ID').text for r in root.iter('Index') if
                                r.find('ReagentKit') is not None)) else '',
                        ),
                        pe=dict(
                            kit=list(root.iter('Pe')).pop(0).text if len(list(root.iter('Pe'))) else '',
                            id=list(r.find('ReagentKit').find('ID').text for r in root.iter('Pe') if
                                    r.find('ReagentKit') is not None).pop() if len(list(
                                r.find('ReagentKit').find('ID').text for r in root.iter('Pe') if
                                r.find('ReagentKit') is not None)) else '',
                        ),
                    ),
                )
            return result

        cmd = 'get_run_parameters'
        params.update(dict(this_run=run))
        res = self._ssh_cmd(user=params.get('user'),
                            host=params.get('host'),
                            cmd=self._get_icmd(cmd=cmd, params=params))

        return _run_parameters_parser(res)

    def _ssh_cmd(self, user, host, cmd):
        remote = "{}@{}".format(user, host)
        ssh = subprocess.Popen(["ssh", remote, cmd],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        result = [line.rstrip('\n') for line in ssh.stdout.readlines()]
        error = ssh.stderr.readlines()

        if error:
            result = dict(success='False', error=error, result=[])
        else:
            result = dict(success='True', error=[], result=result)

        return result

    def _get_icmd(self, cmd, params):

        icmds = dict(
            get_running_folders="ls {} | grep XX".format(params.get('run_folder')),

            get_run_info="cat {}".format(os.path.join(params.get('run_folder', ''),
                                                      params.get('this_run', ''),
                                                      params.get('run_info_file', ''))),

            get_run_parameters="cat {}".format(os.path.join(params.get('run_folder', ''),
                                                            params.get('this_run', ''),
                                                            params.get('run_parameters_file', ''))),

        )

        return icmds.get(cmd)
