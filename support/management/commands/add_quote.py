from django.core.management.base import BaseCommand, CommandError

from support.models import Quote


class Command(BaseCommand):
    help = '''Adds new quote to both the database and data file storing quotes
    for cross server reasons'''

    def add_arguments(self, parser):
        parser.add_argument(
            'body',
            type=str
        )

        parser.add_argument('-a',
            dest='author',
            default='Anonymous',
            help='Name of the author credited with saying quote'
        )

        parser.add_argument('-c',
            dest='category',
            default=Quote.CATEGORIES[0][1],
            help='The category to which the quote belongs'
        )

        parser.add_argument('-f',
            dest='filename',
            default=Quote.quote_datafile,
            help='File name from which to load quotes'
        )

    def handle(self, *args, **kwargs):
        quote = Quote.objects.create(
            body=kwargs['body'],
            author=kwargs['author'],
            category=kwargs['category']
        )

        Quote.write_quotes_to_data(Quote.objects.all(),
        filename=kwargs['filename'])

        self.stdout.write('Successfully added 1 quote to database and file')

