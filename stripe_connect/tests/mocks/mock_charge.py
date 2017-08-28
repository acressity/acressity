from stripe import Charge, convert_to_stripe_object
from stripe.error import InvalidRequestError

class MockCharge(Charge):
    charge_data = [
        { # Successful charge made by explorer_benefactor
            'amount': 0, # This to be modified
            'amount_refunded': 0, 
            'application': 'ca_92N9ZacpBsklBCl8SdAk90sNpcwuUUMd', 
            'application_fee': 'fee_A0fhovzHkRCeOB', 
            'balance_transaction': 'txn_19geMACSxTlkjoJm6YOI24dn', 
            'captured': True, 
            'created': 1485541313, 
            'currency': 'usd', 
            'customer': None, 
            'description': 'Bounty to fulfill: Bounty', 
            'destination': None, 
            'dispute': None, 
            'failure_code': None, 
            'failure_message': None, 
            'fraud_details': {}, 
            'id': 'ch_19geM9CSxTlkjoJm0LJOEeK4', 
            'invoice': None, 
            'livemode': False, 
            'metadata': {}, 
            'object': 'charge', 
            'order': None, 
            'outcome': {
                'network_status': 'approved_by_network', 
                'reason': None, 
                'seller_message': 'Payment complete.', 
                'type': 'authorized'
            }, 
            'paid': True, 
            'receipt_email': None, 
            'receipt_number': None, 
            'refunded': False, 
            'refunds': {
                'data': [], 
                'has_more': False, 
                'object': 'list', 
                'total_count': 0, 
                'url': '/v1/charges/ch_19geM9CSxTlkjoJm0LJOEeK4/refunds'
            }, 
            'review': None, 
            'shipping': None, 
            'source': {
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
                'customer': None, 
                'cvc_check': None, 
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
            'source_transfer': None, 
            'statement_descriptor': None, 
            'status': 'succeeded'
        },
    ]


    @classmethod
    def create(cls, api_key=None, idempotency_key=None, stripe_account=None, **params):
        charge_data = cls.charge_data[0]
        charge_data['amount'] = params.get('amount')
        charge_data['description'] = params.get('description')
        return convert_to_stripe_object(charge_data, api_key, stripe_account)

    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        for charge_data in cls.charge_data:
            if charge_data.get('id') == id:
                return convert_to_stripe_object(charge_data, api_key=None, account=None)
        raise InvalidRequestError
