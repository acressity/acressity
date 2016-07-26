from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from support.models import Quote

class QuoteTest(TestCase):
    test_quote_datafile = 'support/tests/data/quotes.dat'

    def setUp(self):
        # Create a starting quote
        self.quote1 = Quote(
            body='Life begins at the end of your comfort zone',
            author='Neale Donald Walsch'
        )
        self.quote1.save()

        self.quote2 = Quote(
            body='It always seems impossible until it\'s done',
            author='Nelson Mandela'
        ) # quote2 not saved

    def tearDown(self):
        # Empty the data file
        open(self.test_quote_datafile, 'w').close()


    def test_default_category(self):
        self.assertEqual(self.quote1.category, Quote.CATEGORIES[0][0])

    def test_load_and_write_quote_to_datafile(self):
        quotes = Quote.load_quotes_from_data(filename=self.test_quote_datafile)
        self.assertEqual(len(quotes), 0)
        quotes = [self.quote1, self.quote2]
        Quote.write_quotes_to_data(quotes, filename=self.test_quote_datafile)
        quotes = Quote.load_quotes_from_data(filename=self.test_quote_datafile)
        self.assertEqual(len(quotes), 2)

    def test_add_quote_command(self):
        arguments = [self.quote2.body, '-a', self.quote2.author, '-f',
                self.test_quote_datafile]
        out = StringIO()
        self.assertEqual(Quote.objects.count(), 1)
        call_command('add_quote', *arguments, stdout=out)
        self.assertEqual(Quote.objects.count(), 2)
        self.assertIn(self.quote2.body, [q.body for q in Quote.objects.all()])
        self.assertIn('success', out.getvalue().lower())

    def test_load_quotes_command(self):

        # Populate the data file so there is something to load
        Quote.write_quotes_to_data([self.quote1, self.quote2],
                filename=self.test_quote_datafile)

        arguments = ['-f', self.test_quote_datafile]
        out = StringIO()
        self.assertEqual(Quote.objects.count(), 1)
        call_command('load_quotes', *arguments, stdout=out)
        self.assertEqual(Quote.objects.count(), 2)
