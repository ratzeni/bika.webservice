from functools import wraps
from bottle import post, get, run, response, request

from bikaclient import BikaClient


class BikaApiRestService(object):

    def __init__(self):
        pass

    def _get_bika_instance(self, params):
        return BikaClient(host=params.get('bika_host'),
                          username=params.get('bika_user'),
                          password=params.get('bika_passwd'))


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
    def get_clients(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_clients(params)
        return result

    @wrap_default
    def get_samples(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_samples(params)
        return result

    @wrap_default
    def get_analysis_requests(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_analysis_requests(params)
        return result

    @wrap_default
    def get_arimports(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_arimports(params)
        return result

    @wrap_default
    def get_batches(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_batches(params)
        return result

    @wrap_default
    def get_worksheets(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_worksheets(params)
        return result

    @wrap_default
    def get_invoices(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_invoices(params)
        return result

    @wrap_default
    def get_price_list(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_price_list(params)
        return result

    @wrap_default
    def get_supply_order(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_supply_order(params)
        return result

    @wrap_default
    def get_artemplates(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_artemplates(params)
        return result

    @wrap_default
    def get_analysis_profiles(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_analysis_profiles(params)
        return result

    @wrap_default
    def get_analysis_services(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_analysis_services(params)

    @wrap_default
    def get_sample_types(self):
        params = request.query
        bika = self._get_bika_instance(params)
        result = bika.get_sample_types(params)
        return result


