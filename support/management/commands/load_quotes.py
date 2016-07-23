from django.core.management.base import BaseCommand, CommandError

from support.models import Quote


class Command(BaseCommand):
    help = 'Loads quotes currently in data file, deleting old ones first'

    def add_arguments(self, parser):
        parser.add_argument('-f',
            dest='filename',
            default=Quote.quote_datafile,
            help='File name from which to load quotes'
        )

    def handle(self, *args, **kwargs):
        acressity_quotes = Quote.load_quotes_from_data(kwargs['filename'])
        Quote.objects.all().delete()
        
        num_quotes = 0
        for quote in acressity_quotes:
            quote.save()
            num_quotes += 1
        
        self.stdout.write('Successfully loaded {0} quotes'.format(num_quotes))
