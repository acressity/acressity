from stripe import Account, convert_to_stripe_object
from stripe.error import InvalidRequestError


class MockAccount(Account):
    account_data = [
        { # Account data for explorer_author
            'business_logo': None, 
            'business_name': None, 
            'business_url': 'Author', 
            'charges_enabled': True, 
            'country': 'US', 
            'default_currency': 'usd', 
            'details_submitted': True, 
            'display_name': 'Author', 
            'email': 'author@mail.com', 
            'id': 'acct_18knOdCSxTlkjoJm', 
            'managed': False, 
            'metadata': {}, 
            'object': 'account', 
            'statement_descriptor': 'Author', 
            'support_email': None, 
            'support_phone': '4654684684', 
            'timezone': 'America/Denver', 
            'transfers_enabled': True
        },
        { # Account data for explorer_benefactor
            'business_logo': None, 
            'business_name': None, 
            'business_url': 'Benefactor', 
            'charges_enabled': True, 
            'country': 'US', 
            'default_currency': 'usd', 
            'details_submitted': True, 
            'display_name': 'Benefactor', 
            'email': 'benefactor@mail.com', 
            'id': 'acct_29knOdCSxTlkjoKn', 
            'managed': False, 
            'metadata': {}, 
            'object': 'account', 
            'statement_descriptor': 'Benefactor', 
            'support_email': None, 
            'support_phone': '5654684685', 
            'timezone': 'America/Denver', 
            'transfers_enabled': True
        },
    ]

    @classmethod
    def create(cls, api_key=None, idempotency_key=None, stripe_account=None, **params):
        raise NotImplementedError
        #return convert_to_stripe_object(self.account_data[0], api_key, account_id)

    @classmethod
    def retrieve(cls, id=None, api_key=None, **params):
        for account_data in cls.account_data:
            if account_data.get('id') == id:
                return convert_to_stripe_object(account_data, api_key, id)
        raise InvalidRequestError
