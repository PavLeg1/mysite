from django import template
from ..models import Post
from django.db.models import Count 
from django.utils.safestring import mark_safe
import markdown


# Переменная, необходимая для создания / регистрации своих шаблонных тегов
register = template.Library()

# Простой шаблонный тег, возвращающий кол-во опубликованных постов
@register.simple_tag             # Декоратор регистрирует функцию как simple_tag. При необходимости задать другое имя: @register.simple_tag(name='tag_name')
def total_posts():               
    return Post.published.count()

# теги включения возвращают словарь значений, используемый в качестве контекста для прорисовки заданного шаблона 
@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    # С помощью annotate() формируется QuerySet, чтобы рассчитать кол-во комментов к посту
    return Post.published.annotate(total_comments = Count('comments')).order_by('-total_comments')[:count]

@register.filter(name='markdown') # Имя которое используется в шаблоне {{ variable|markdown }}
# Функция помечает результат как безопасный для прорисовки в шаблоне 
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
