from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template_from_string

from explorers.models import Explorer

html_content = '''
    <h3>Greetings, {{ explorer.get_full_name }}</h3>
    <p>
        It's good to have you on the site! I hope it helps facilitate following through on exploring your experiences somehow. The world feels so open when you travel beyond a former limit despite the discomfort.
    </p>
    <p>
        Build your list of experiences on your <a href="http://acressity.com{% url 'journey' explorer.id %}">journey</a> page.
    </p>
    {% if explorer.featured_experience %}
        <p>Write a narrative about your featured experience "{{ explorer.featured_experience }}" <a href="{% url 'create_narrative' explorer.featured_experience.id %}">here</a>
        </p>
    {% endif %}
    <p>
        I apologize if this email is unbecoming or intrusive. I only wish to share my excitement at having you be a part of the site I built in hopes of facilitating some neat experiences. Being a relatively young site, I am open to any suggestions and comments you may have. I can be reached through the address acressity@acressity.com
    </p>
    <p>
        Happy trails!
    </p>
    '''
text_content = '''Greetings, {{ explorer.get_full_name }}\n\n\nIt's good to have you on the site! I hope it helps facilitate following through on exploring your experiences somehow. The world feels so open when you travel beyond a former limit despite the discomfort.\n\nBuild your list of experiences on your journey page at http://acressity.com{% url 'journey' explorer.id %}.\n\nI apologize if this email is unbecoming or intrusive. I only wish to share my excitement at having you be a part of the site I built in hopes of facilitating some neat experiences. Being a relatively young site, I am open to any suggestions and comments you may have. I can be reached through the address acressity@acressity.com\n\nHappy trails!'''

eo = [Explorer.objects.get(pk=1)]

for explorer in eo:
    context = Context({'explorer': explorer})
    html_t = get_template_from_string(html_content)
    text_t = get_template_from_string(text_content)
    text_message = text_t.render(context)
    html_message = html_t.render(context)
    m = EmailMultiAlternatives('Greetings from Acressity', text_message, 'acressity@acressity.com', [explorer.email])
    m.attach_alternative(html_message, 'text/html')
    print(explorer, m.send())
