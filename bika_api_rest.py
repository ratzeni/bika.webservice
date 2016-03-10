from functools import wraps
from bottle import post, get, run, response, request

from bikaclient import BikaClient


class BikaApiRestService(object):

    def __init__(self):
        self.user_roles = ['Site Administrator', 'LabManager', 'Analyst', 'LabClerk', 'Client']
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
    def login(self):
        params = request.query
        bika = self._get_bika_instance(params)
        login_test = bika.get_clients(params)
        if 'objects' in login_test and len(login_test['objects']) > 0:

            user = params.get('bika_user')
            for role in self.user_roles:
                params['roles']=role
                res = bika.get_users(self._format_params(params))
                if 'users' in res:
                    for r in res['users']:
                        if user in r['fullname']:
                            result = dict(
                                userid=str(r['userid']),
                                fullname=str(r['fullname']),
                                role=role,
                            )

                            return dict(user=result,
                                        is_signed='True',
                                        success=str(res['success']), error=str(res['error']))

        return dict(user=[],
                    is_signed='False',
                    success='False', error='True')

    @wrap_default
    def get_clients(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_clients(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['Title']),
                client_id=str(r['ClientID']),
                path=str(r['path'])) for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def get_contacts(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_contacts(params)
        client_id = params.get('client_id', '')
        result = [dict(
                id=str(r['id']),
                title=str(r['Title']),
                email_address=str(r['EmailAddress']),
                path=str(r['path'])) for r in res['objects'] if client_id in r['path']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

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
        res = bika.get_analysis_requests(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['Title']),
                sample_id=str(r['SampleID']),
                sample_type=str(r['SampleTypeTitle']),
                path=str(r['path']),
                client_sample_id=str(r['ClientSampleID']),
                client=str(r['Client']),
                contact=str(r['Contact']),
                cccontact=[str(c) for c in r['CCContact']],
                batch_id=str(r['title']),
                batch_title=str(r['Batch']),
                date=str(r['Date']),
                date_received=str(r['DateReceived']),
                date_published=str(r['DatePublished']),
                date_created=str(r['creation_date']),
                review_state=str(r['review_state']),
                remarks=str(r['Remarks']),
                results_interpretation=str(r['ResultsInterpretation']),
                params=self._get_environmental_conditions(r['EnvironmentalConditions']),
                creator=str(r['Creator']),
                analyses=self._get_analyses(r['Analyses']),
                transitions=[dict(id=str(t['id']), title=str(t['title'])) for t in r['transitions']],
                )for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

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
        res = bika.get_batches(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['Title']),
                description=str(r['description']),
                path=str(r['path']),
                client_batch_id=str(r['ClientBatchID']),
                client=str(r['Client']),
                date=str(r['Date']),
                creation_date=str(r['creation_date']),
                modification_date=str(r['modification_date']),
                review_state=str(r['review_state']),
                remarks=str(r['Remarks']),
                uid=str(r['UID']),
                creator=str(r['Creator']),
                cost_center=str(r['rights']),
                transitions=[dict(id=str(t['id']), title=str(t['title'])) for t in r['transitions']],
                )for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def get_worksheets(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_worksheets(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['title']),
                description=str(r['description']),
                path=str(r['path']),
                analyst=str(r['Analyst']),
                instrument=str(r['Instrument']),
                creation_date=str(r['creation_date']),
                modification_date=str(r['modification_date']),
                date=str(r['Date']),
                remarks=str(r['Remarks']),
                review_state=str(r['subject'][0]) if len(r['subject'])==1 else '',
                uid=str(r['UID']),
                creator=str(r['Creator']),
                transitions=[dict(id=str(t['id']), title=str(t['title'])) for t in r['transitions']],
        ) for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

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
    def get_supply_orders(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_supply_orders(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['title']),
                description=str(r['description']),
                path=str(r['path']),
                creation_date=str(r['creation_date']),
                modification_date=str(r['modification_date']),
                expiration_date=str(r['expirationDate']),
                dispatched_date=str(r['DateDispatched']),
                order_date=str(r['OrderDate']),
                date=str(r['Date']),
                order_number=str(r['OrderNumber']),
                location=str(r['location']),
                rights=str(r['rights']),
                remarks=str(r['Remarks']),
                invoice=str(r['Invoice']),
                client_id=str(r['path']).split('/')[-2],
                review_state=str(r['subject'][0]) if len(r['subject'])==1 else '',
                uid=str(r['UID']),
                creator=str(r['Creator']),
                transitions=[dict(id=str(t['id']), title=str(t['title'])) for t in r['transitions']],
        ) for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

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
        res = bika.get_analysis_profiles(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['Title']),
                total_price=str(r['TotalPrice']),
                path=str(r['path']),
                services_data=self._get_service_data(r['AnalysisServicesSettings'])
                )for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def get_analysis_services(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res= bika.get_analysis_services(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['Title']),
                keyword=str(r['Keyword']),
                total_price=str(r['TotalPrice']),
                price=str(r['Price']),
                category=str(r['CategoryTitle']),
                path=str(r['path']),
                ) for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))


    @wrap_default
    def get_sample_types(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_sample_types(params)
        result = [dict(
                id=str(r['id']),
                title=str(r['Title']),
                container_type=str(r['ContainerType']),
                prefix=str(r['Prefix']),
                ) for r in res['objects']]

        return dict(objects=result, total=str(res['total_objects']),
                    first=str(res['first_object_nr']), last=str(res['last_object_nr']),
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def count_samples(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_samples(params)
        result = str(res['total_objects'])
        return result

    @wrap_default
    def count_analysis_requests(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_analysis_requests(params)
        result = str(res['total_objects'])
        return result

    @wrap_default
    def create_batch(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.create_batch(self._format_params(params))
        return self._outcome_creating(res, params)

    @wrap_default
    def create_analysis_request(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.create_analysis_request(self._format_params(params))
        return self._outcome_creating(res, params)

    @wrap_default
    def create_worksheet(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.create_worksheet(self._format_params(params))
        return self._outcome_creating(res, params)

    @wrap_default
    def create_supply_order(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.create_supply_order(self._format_params(params))
        return self._outcome_creating(res, params)

    @wrap_default
    def cancel_batch(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.cancel_batch(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def cancel_worksheet(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.cancel_worksheet(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def cancel_analysis_request(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.cancel_analysis_request(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def reinstate_batch(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.reinstate_batch(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def reinstate_worksheet(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.reinstate_worksheet(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def reinstate_analysis_request(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.reinstate_analysis_request(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def open_batch(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.open_batch(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def close_batch(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.close_batch(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def open_worsheet(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.open_worsheet(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def close_worsheet(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.close_worsheet(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def receive_sample(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.receive_sample(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def submit(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.submit(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def verify(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.verify(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def publish(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.publish(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def activate_supply_order(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.activate_supply_order(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def deactivate_supply_order(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.deactivate_supply_order(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def dispatch_supply_order(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.dispatch_supply_order(self._format_params(params))
        return self._outcome_action(res, params)

    @wrap_default
    def set_analysis_result(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def set_analyses_results(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update_many(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def get_users(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_users(self._format_params(params))
        result = [dict(
                userid=str(r['userid']),
                fullname=str(r['fullname']),
        ) for r in res['users']]

        return dict(objects=result,
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def get_manager_users(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_manager_users()
        result = [dict(
                userid=str(r['userid']),
                fullname=str(r['fullname']),
        ) for r in res['users']]

        return dict(objects=result,
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def get_analyst_users(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_analyst_users()
        result = [dict(
                userid=str(r['userid']),
                fullname=str(r['fullname']),
        ) for r in res['users']]

        return dict(objects=result,
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def get_clerk_users(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_clerk_users()
        result = [dict(
                userid=str(r['userid']),
                fullname=str(r['fullname']),
        ) for r in res['users']]

        return dict(objects=result,
                    success=str(res['success']), error=str(res['error']))

    @wrap_default
    def get_client_users(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.get_client_users()
        result = [dict(
                userid=str(r['userid']),
                fullname=str(r['fullname']),
        ) for r in res['users']]

        return dict(objects=result,
                    success=str(res['success']), error=str(res['error']))


    @wrap_default
    def update_batch(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def update_batches(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update_many(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def update_analysis_request(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def update_analysis_requests(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update_many(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def update_worksheet(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def update_worksheets(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update_many(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def update_supply_order(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update(self._format_params(params))
        return self._outcome_update(res, params)

    @wrap_default
    def update_supply_orders(self):
        params = request.query
        bika = self._get_bika_instance(params)
        res = bika.update_many(self._format_params(params))
        return self._outcome_update(res, params)

    def _get_analysis_requests(self, batch_id):
        params = request.query
        bika = self._get_bika_instance(params)
        this_params = dict(title= batch_id, include_fields='id')
        res = bika.get_analysis_requests(this_params)
        return [dict(
                id=str(r['id']),
                path=str(r['path']),
        )for r in res['objects']]

    def _get_analyses(self, analyses):
        return [dict(
                id=str(r['id']),
                title=str(r['Title']),
                description=str(r['description']),
                keyword=str(r['Keyword']),
                category=str(r['CategoryTitle']),
                result=str(r['Result']),
                client=str(r['ClientTitle']),
                due_date=str(r['DueDate']),
                date_received=str(r['DateReceived']),
                date_sampled=str(r['DateSampled']),
                date_pubblished=str(r['DateAnalysisPublished']),
                result_date=str(r['ResultCaptureDate']),
                analyst=str(r['Analyst']),
                request_id=str(r['RequestID']),
                review_state=str(r['review_state']),
                remarks=str(r['Remarks']),
                uid=str(r['UID']),
                transitions=[dict(id=str(t['id']), title=str(t['title'])) for t in r['transitions']],
        )for r in analyses]

    def _get_service_data(self, analysis_services_settings):
        for settings in analysis_services_settings:
            if 'service_data' in settings:
                services_data = [dict(
                    id=str(s['id']),
                    title=str(s['Title']),
                    price=str(s['Price']),
                    path=str(s['path']),
                ) for s in settings['service_data']]
                return services_data
        return []

    def _get_environmental_conditions(self, str_environmental_conditions):
        environmental_conditions = list()
        for ec in str_environmental_conditions.split('|'):
            items = ec.split('=')
            if len(items) == 2:
                environmental_conditions.append(dict(label=str(items[0]), value=str(items[1])))
        return  environmental_conditions

    def _format_params(self, params):
        mirror = dict(params)
        del mirror['bika_host']
        del mirror['bika_user']
        del mirror['bika_passwd']
        del mirror['callback']

        return mirror

    def _outcome_creating(self, res, params):
        result = None
        if 'obj_id' in res:
            result = dict(success='True', obj_id=str(res['obj_id']))
        elif 'ar_id' in res and 'sample_id' in res:
            result = dict(success='True', ar_id=str(res['ar_id']), sample_id=str(res['sample_id']))
        elif 'message' in res:
            result = dict(success='False', message=str(res['message']))

        if not result:
            result = res
        return result

    def _outcome_action(self, res, params):
        result = None
        if 'message' in res:
            result = dict(success='False', message=str(res['message']))
        else:
            result = dict(success='True')

        return result

    def _outcome_update(self, res, params):
        result = None
        if 'message' in res:
            result = dict(success='False', message=str(res['message']))
        else:
            result = dict(success='True', updates=[{str(k): str(v)}  for t in res['updates'] for k,v in t.iteritems()] if 'updates' in res else list())

        if not result:
            result = res

        return result