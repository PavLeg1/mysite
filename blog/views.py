from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

def post_list(request):
    post_list = Post.published.all()
    # Постраничная разбивка с 3 постами на страницу
    # Создаем экземпляр класса Paginator с числом объектов на странице (у нас это по три поста на странице)
    paginator = Paginator(post_list, 3)
    # Извлекаем HTTP GET-параметр page и сохраняем его в page_number
    page_number = request.GET.get('page', 1)
    
    try:
        # Возвращаем объект Page хранящийся в переменной posts
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # Если page не число - выдаем первую страницу
        posts = paginator.page(1) 
    except EmptyPage:
        # Если page_number вне диапазона - выдаем последнюю страницу
        posts = paginator.page(paginator.num_pages)

    # Передаем номер страницы и объект posts в шаблон
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})


def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No post found.")
    # URL состоит из даты и слага
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})


class PostListView(ListView):
    queryset = Post.published.all() # Используется для того, чтобы иметь конкретно-прикладной набор запросов QuerySet, не извлекая все объекты
    context_object_name = 'posts'   # 'posts' используется для результатов запроса. Если в context_object_name ничего не указано, по умолчанию object_list 
    paginate_by = 3                 # В данном атрибуте задается постраничная разбивка результатов с возвратом трех объектов на страницу    
    template_name = 'blog/post/list.html' # Конкретно-прикладной шаблон используется для прорисовки страницы шаблоном template_name     