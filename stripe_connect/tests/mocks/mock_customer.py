import random
import time

from stripe import Customer, convert_to_stripe_object
from stripe.error import CardError, InvalidRequestError
from stripe_connect.tests.helpers import random_string


class MockCustomer(Customer):
    customer_data = [
        { # Customer data for exporer_author
            'account_balance': 0, 
            'created': 1485287909, 
            'currency': None, 
            'default_source': None, 
            'delinquent': False, 
            'description': 'author@mail.com', 
            'discount': None, 
            'email': None, 
            'id': 'cus_9zZaZKg1AE04Vh', 
            'livemode': False, 
            'metadata': {}, 
            'object': 'customer', 
            'shipping': None, 
            'sources': {
                'data': [], 
                'has_more': False, 
                'object': 'list', 
                'total_count': 0, 
                'url': '/v1/customers/cus_9zZaZKg1AE04Vh/sources'
            }, 
            'subscriptions': {
            'data': [], 
            'has_more': False, 
            'object': 'list', 
            'total_count': 0, 
            'url': '/v1/customers/cus_9zZaZKg1AE04Vh/subscriptions'
          }
        },
        { # Customer data for exporer_benefactor
            'account_balance': 0, 
            'created': 1485287888, 
            'currency': None, 
            'default_source': 'card_19faSHIWMPrMK1Ezw3YAGfPh', 
            'delinquent': False, 
            'description': 'benefactor@mail.com', 
            'discount': None, 
            'email': None, 
            'id': 'cus_9zZZGyWNQVLGTr', 
            'livemode': False, 
            'metadata': {}, 
            'object': 'customer', 
            'shipping': None, 
            'sources': {
                'data': [
                    {
                        'address_city': None, 
                        'address_country': None, 
                        'address_line1': None, 
                        'address_line1_check': None, 
                        'address_line2': None, 
                        'address_state': None, 
                        'address_zip': '56566', 
                        'address_zip_check': 'pass', 
                        'brand': 'Visa', 
                        'country': 'US', 
                        'customer': 'cus_9zZZGyWNQVLGTr', 
                        'cvc_check': 'pass', 
                        'dynamic_last4': None, 
                        'exp_month': 5, 
                        'exp_year': 2022, 
                        'fingerprint': 'wriEmgPG57lHF8em', 
                        'funding': 'credit', 
                        'id': 'card_19faSHIWMPrMK1Ezw3YAGfPh', 
                        'last4': '4242', 
                        'metadata': {}, 
                        'name': 'benefactor@mail.com', 
                        'object': 'card', 
                        'tokenization_method': None
                    }, 
                ], 
                'has_more': False, 
                'object': 'list', 
                'total_count': 2, 
                'url': '/v1/customers/cus_9zZZGyWNQVLGTr/sources'
            }, 
            'subscriptions': {
            'data': [], 
            'has_more': False, 
            'object': 'list', 
            'total_count': 0, 
            'url': '/v1/customers/cus_9zZZGyWNQVLGTr/subscriptions'
            }
        },
    ]

    @classmethod
    def create(cls, api_key=None, idempotency_key=None, stripe_account=None, **params):
        # Build new random id
        customer_id = 'cus_' + random_string(14)
        customer_url = '/v1/customers/{0}/sources'.format(customer_id)

        # Build customer data from framework of first dictionary
        customer_data = cls.customer_data[0]
        customer_data['id'] = customer_id
        customer_data['url'] = customer_url
        customer_data['sources']['url'] = customer_url
        customer_data['created'] = int(time.time())
        customer_data['description'] = params.get('description')

        # Add new data to customer_data for future retrieval purposes
        cls.customer_data.append(customer_data)
        return convert_to_stripe_object(customer_data, api_key, stripe_account)

    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        for customer_data in cls.customer_data:
            if customer_data.get('id') == id:
                return convert_to_stripe_object(customer_data, api_key=None, account=None)
        raise InvalidRequestError('Could not find valid Customer', 'id')
