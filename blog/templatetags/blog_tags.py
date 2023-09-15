from django import template
from ..models import Post

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

    