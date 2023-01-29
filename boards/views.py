from django.utils import timezone
from django.shortcuts import get_object_or_404, render ,redirect

from boards.forms import NewTopicForm ,PostForm
from .models import Board, Topic,Post
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.

def home(request):
    boards=Board.objects.all()
    return render(request ,'home.html',{'boards':boards} )

# def board_topics(request,board_id):
#     # try:
#     #     board = Board.objects.get(pk=board_id)
#     # except Board.DoesNotExist:
#     #     raise Http404
#     board = get_object_or_404(Board,pk=board_id)
#     topics = board.topics.order_by("-created_dt").annotate(comments=Count('posts'))
#     return render(request,'topics.html',{'board':board , 'topics':topics})

def board_topics(request,board_id):

    board = get_object_or_404(Board,pk=board_id)
    queryset = board.topics.order_by('-created_dt').annotate(comments=Count('posts'))
    page = request.GET.get('page',1)
    paginator = Paginator(queryset,5)
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)
    return render(request,'topics.html',{'board':board,'topics':topics})    



@login_required
def new_topic(request,board_id):
    board = get_object_or_404(Board,pk=board_id)
   # user = User.objects.first()
    if request.method == "POST":
        form =NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.created_by = request.user
            topic.save()

            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                created_by = request.user,
                topic=topic

            )
            return redirect('boards:board_topics',board_id=board.pk)
    else:
        form = NewTopicForm()

    return render(request,'new_topic.html',{'board':board,'form':form})

# def topic_posts(request,board_id,topic_id):
#     topic = get_object_or_404(Topic,board__pk=board_id,pk=topic_id)
#     topic.views+=1
#     topic.save()
#     return render(request,'topic_posts.html',{'topic':topic})
def topic_posts(request,board_id,topic_id):
    topic = get_object_or_404(Topic,board__pk=board_id,pk=topic_id)

    session_key = 'view_topic_{}'.format(topic.pk)
    if not request.session.get(session_key,False):
        topic.views +=1
        topic.save()
        request.session[session_key] = True
    return render(request,'topic_posts.html',{'topic':topic})

@login_required
def reply_topic(request, board_id,topic_id):
    topic = get_object_or_404(Topic,board__pk=board_id,pk=topic_id)
    if request.method == "POST":
        form =PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            return redirect('boards:topic_posts',board_id=board_id, topic_id = topic_id)
    else:
        form = PostForm()
    return render(request,'reply_topic.html',{'topic':topic,'form':form})


class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post' 

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_dt = timezone.now()
        post.save()
        return redirect('boards:topic_posts',board_id=post.topic.board.pk,topic_id=post.topic.pk) 

def about(request):

    return HttpResponse(request,"yes")
        