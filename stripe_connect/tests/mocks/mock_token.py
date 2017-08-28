from stripe import Token, convert_to_stripe_object
from stripe.error import CardError, InvalidRequestError
from stripe_connect.tests.helpers import random_string


class MockToken(Token):
    token_data = [
        {
            'card': {
                'address_city': None,
                'address_country': None,
                'address_line1': None,
                'address_line1_check': None,
                'address_line2': None,
                'address_state': None,
                'address_zip': None,
                'address_zip_check': None,
                'brand': 'Visa',
                'country': 'US',
                'cvc_check': 'unchecked',
                'dynamic_last4': None,
                'exp_month': 5,
                'exp_year': 2022,
                'fingerprint': 'wriEmgPG57lHF8em',
                'funding': 'credit',
                'id': 'card_19faSHIWMPrMK1Ezw3YAGfPh',
                'last4': '4242',
                'metadata': {},
                'name': None,
                'object': 'card',
                'tokenization_method': None
            },
            'client_ip': '192.168.1.1',
            'created': 1453817861,
            'id': 'tok_42XXdZGzvyST06Z0LA6h5gJp',
            'livemode': False,
            'object': 'token',
            'type': 'card',
            'used': False,
        },
        {
            'card': {
                'address_city': None,
                'address_country': None,
                'address_line1': None,
                'address_line1_check': None,
                'address_line2': None,
                'address_state': None,
                'address_zip': None,
                'address_zip_check': None,
                'brand': 'Visa',
                'country': 'US',
                'cvc_check': 'unchecked',
                'dynamic_last4': None,
                'exp_month': 12,
                'exp_year': 2018,
                'fingerprint': '39fS1c4ThLaGETbt',
                'funding': 'credit',
                'id': 'card_29XXdZGzVYST06Z022EiG1ze',
                'last4': '4242',
                'metadata': {},
                'name': None,
                'object': 'card',
                'tokenization_method': None
            },
            'client_ip': '192.168.1.1',
            'created': 1453817862,
            'id': 'tok_32XXdZGzvyST06Z0LA6h5gJj',
            'livemode': False,
            'object': 'token',
            'type': 'card',
            'used': False,
        },
    ]

    @classmethod
    def create(cls, api_key=None, idempotency_key=None, stripe_account=None, **params):
        # Build new random id
        token_id = 'tok_' + random_string(24)

        # Build token data from framework of first dictionary
        token_data = cls.token_data[0]
        token_data['id'] = token_id

        # Link the new token/source to customer.sources
        #customer = stripe.Customer.retrieve(
            #params.get('customer')
        #)
        #customer.sources.create(
            #source=token_id
        #)

        # Add new data to token_data for future retrieval purposes
        cls.token_data.append(token_data)
        return convert_to_stripe_object(token_data, api_key, stripe_account)

    @classmethod
    def retrieve(cls, id, api_key=None, stripe_account=None, **params):
        for token_data in cls.token_data:
            if id == token_data.get('id'):
                return convert_to_stripe_object(token_data, api_key, stripe_account)
        raise InvalidRequestError('Could not find valid Token', 'id')

