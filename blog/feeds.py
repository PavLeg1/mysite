import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post


class LatestPostsFeed(Feed):
    # RSS элементы
    title = 'My blog'
    link = reverse_lazy('blog:post_list') # генерация URL для атрибута link
    description = 'New posts of my blog.'

    # Извлечение объектов новостной ленты
    def items(self):
        return Post.published.all()[:5]
    
    # Данные методы получают объект от метода items() и возвращают title, link и description соответственно
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)
    
    def item_pubdate(self, item):
        return item.publish