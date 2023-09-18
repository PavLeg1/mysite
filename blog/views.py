from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag 
from django.db.models import Count # Подсчет общего количества объектов
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag=None
    # Внутри этого представления формируется набор запросов, извлекающий все опубликованные посты, если имеется слаг этого тега - берется объект Tag с данным слагом
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag]) # Операция __in - поиск по полю

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

    # Передаем номер страницы, объект posts и теги tag в шаблон
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'tags': tag})


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
    # Список активных комментариев к посту:
    # Добавлен набор запросов QuerySet чтобы извлекать все активные комментарии к посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()

    # Список схожих постов
    # values_list возвращает кортежи со значениями заданных полей. Если передается flat=True передаются одиночные значения [1, 2, 3] вместо [(1,), (2,), (3,)]
    # Далее берутся все посты с этими тегами, кроме текущего, применяется Count. Генерирует поле same_tags содержащее кол-во общих тегов
    # Результат упорядочивается по числу общих тегов (в убывающем порядке) и по publish (если одинаковое кол-во тегов сначала отображаются последние посты)
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4] # Получаем выборку из 4 предложенных постов

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})

# Представление для отправки поста получая доступ к посту через его id используя функцию get_object_or_404()
def post_share(request, post_id):
    # Извлечь пост по id
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    
    # Еще не было отправлено
    sent = False
    
    
    if request.method == 'POST':
        # Форма была передана на обработку с данными из request.POST
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data

            # Получаем путь до поста чтобы его отправить
            post_url = request.build_absolute_uri(post.get_absolute_url())
            
            # Тема письма
            subject = f"{cd['name']} recommends you to read {post.title}"
            
            # Текст письма с комментом (если есть) 
            message = f"Read {post.title} at {post_url}\n\n\
                {cd['name']} comments: {cd['comments']}"
            send_mail(subject, message, 'pvlegostaev@gmail.com', [cd['to']])

            # Письмо отправлено
            sent = True 
    else:
        # Отображение пустой формы если метод "GET"
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


# Вариант со взвешиванием 
def post_search(request):
    # Создаем экземпляр формы SearchForm
    form = SearchForm()
    query = None
    results = []

    # Проверка, что форма была передана на обработку
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # Веса: A == 1.0, B == 0.4, C == 0.2, D == 0.1
            # При rank__gte=0.3 результаты фильтруются чтобы отображать только те, у которых ранг выше 0.3
            search_vector = SearchVector('title', weight = 'A') + \
                            SearchVector('body', weight = 'B') # Через аргумент config передается язык - стемминг слов
            # Создается объект SearchQuery  
            search_query = SearchQuery(query, config='spanish') # Через аргумент config передается язык - удаление стоп-слов этого языка
            # Выполняется поиск опубликованных постов по запросу
            # По объекту SearchQuery фильтруются результаты и для упорядочивания используется SearchRank 
            results = Post.published.annotate(search = search_vector, 
                                              rank=SearchRank(search_vector,
                                                              search_query)).filter(rank__gte=0.3).order_by('-rank') # Поиск со взвешиванием слов 

    
    return render(request, 'blog/post/search.html', 
                  {'form': form,
                   'query': query,
                   'results': results})
'''
# Реализация триграммного поиска
def post_search(request):
    # Создаем экземпляр формы SearchForm
    form = SearchForm()
    query = None
    results = []

    # Проверка, что форма была передана на обработку
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity') 

    
    return render(request, 'blog/post/search.html', 
                  {'form': form,
                   'query': query,
                   'results': results})





                   
'''


class PostListView(ListView):
    queryset = Post.published.all() # Используется для того, чтобы иметь конкретно-прикладной набор запросов QuerySet, не извлекая все объекты
    context_object_name = 'posts'   # 'posts' используется для результатов запроса. Если в context_object_name ничего не указано, по умолчанию object_list 
    paginate_by = 3                 # В данном атрибуте задается постраничная разбивка результатов с возвратом трех объектов на страницу    
    template_name = 'blog/post/list.html' # Конкретно-прикладной шаблон используется для прорисовки страницы шаблоном template_name     


# Представление управляющее передачей поста на обработку через POST
# Декоратор @require_POST разрешает запросы через POST только для этого представления
# При запросах через другие методы --> ошибка 405
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    # Переменная для хранения комментария при его создании
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базу данных (метод save())
        # save() недоступен для экземпляров Form, так как они не привязаны к конкретной модели 
        comment = form.save(commit=False)
        # Назначить пост комментария
        comment.post = post
        # Сохранить комментарий в БД
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})