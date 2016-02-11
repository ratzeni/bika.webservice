#!/usr/bin/env python

import argparse, daemon, json, sys
try:
    from daemon.pidlockfile import PIDLockFile
except ImportError:
    from lockfile.pidlockfile import PIDLockFile


from bottle import post, get, run, response, request

from bika_api_rest import BikaApiRestService

class BikaService(object):

    def __init__(self, bikaApi):
        # Web service methods
        get('/bika/login')(bikaApi.login)
        get('/bika/get/clients')(bikaApi.get_clients)
        get('/bika/get/contacts')(bikaApi.get_contacts)
        get('/bika/get/samples')(bikaApi.get_samples)
        get('/bika/get/analysis_requests')(bikaApi.get_analysis_requests)
        get('/bika/get/arimports')(bikaApi.get_arimports)
        get('/bika/get/batches')(bikaApi.get_batches)
        get('/bika/get/worksheets')(bikaApi.get_worksheets)
        get('/bika/get/invoices')(bikaApi.get_invoices)
        get('/bika/get/price_list')(bikaApi.get_price_list)
        get('/bika/get/supply_order')(bikaApi.get_supply_order)
        get('/bika/get/artemplates')(bikaApi.get_artemplates)
        get('/bika/get/analysis_profiles')(bikaApi.get_analysis_profiles)
        get('/bika/get/analysis_services')(bikaApi.get_analysis_services)
        get('/bika/get/sample_types')(bikaApi.get_sample_types)
        get('/bika/get/users')(bikaApi.get_users)
        get('/bika/get/manager_users')(bikaApi.get_manager_users)
        get('/bika/get/analyst_users')(bikaApi.get_analyst_users)
        get('/bika/get/clerk_users')(bikaApi.get_clerk_users)
        get('/bika/get/client_users')(bikaApi.get_client_users)

        get('/bika/set/analysis_result')(bikaApi.set_analysis_result)
        get('/bika/set/analyses_results')(bikaApi.set_analyses_results)

        get('/bika/update/batch')(bikaApi.update_batch)
        get('/bika/update/batches')(bikaApi.update_batches)
        get('/bika/update/analysis_request')(bikaApi.update_analysis_request)
        get('/bika/update/analysis_requests')(bikaApi.update_analysis_requests)
        get('/bika/update/worksheet')(bikaApi.update_worksheet)
        get('/bika/update/worksheets')(bikaApi.update_worksheets)

        get('/bika/cancel/batch')(bikaApi.cancel_batch)
        get('/bika/cancel/worksheet')(bikaApi.update_worksheets)
        get('/bika/cancel/analysis_request')(bikaApi.cancel_analysis_request)
        get('/bika/reinstate/batch')(bikaApi.reinstate_batch)
        get('/bika/reinstate/worksheet')(bikaApi.update_worksheets)
        get('/bika/reinstate/analysis_request')(bikaApi.reinstate_analysis_request)

        get('/bika/action/receive_sample')(bikaApi.receive_sample)
        get('/bika/action/close_batch')(bikaApi.close_batch)
        get('/bika/action/open_batch')(bikaApi.open_batch)
        get('/bika/action/close_worksheet')(bikaApi.update_worksheets)
        get('/bika/action/open_worksheet')(bikaApi.update_worksheets)
        get('/bika/action/submit')(bikaApi.submit)
        get('/bika/action/verify')(bikaApi.verify)
        get('/bika/action/publish')(bikaApi.publish)

        get('/bika/create/batch')(bikaApi.create_batch)
        get('/bika/create/analysis_request')(bikaApi.create_analysis_request)
        get('/bika/create/worksheet')(bikaApi.create_worksheet)

        get('/bika/count/analysis_requests')(bikaApi.count_analysis_requests)
        get('/bika/count/samples')(bikaApi.count_samples)

        # check status
        post('/check/status')(self.test_server)
        get('/bika/check/status')(bikaApi.test_server)


    def test_server(self):
        return json.dumps({'status':'Server running'})


    def start_service(self, host, port, logfile, pidfile, server, debug=False):
        log = open(logfile, 'a')
        pid =PIDLockFile(pidfile)
        with daemon.DaemonContext(stderr=log, pidfile=pid):
            run(host=host, port=port, server=server, debug=debug)


def get_parser():
    parser = argparse.ArgumentParser('Run the Bika Lims HTTP server')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='web service binding host')
    parser.add_argument('--port', type=int, default='8088',
                        help='web service binding port')
    parser.add_argument('--server', type=str, default='wsgiref',
                        help='server library (use paste for multi-threaded backend)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable web server DEBUG mode')
    parser.add_argument('--pid-file', type=str,
                        help='PID file for the service daemon',
                        default='/tmp/bika_service.pid')
    parser.add_argument('--log-file', type=str,
                        help='log file for the service daemon',
                        default='/tmp/bika_service.log')
    return parser


def main(argv):
    parser = get_parser()
    args = parser.parse_args(argv)

    bikaApi = BikaApiRestService()

    bikaService = BikaService(bikaApi=bikaApi)

    bikaService.start_service(args.host, args.port, args.log_file, args.pid_file,
                              args.server, args.debug)




if __name__ == '__main__':
    main(sys.argv[1:])
