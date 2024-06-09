from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Post, Comment, Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import PostCreateUpdateForm, CommentCreateForm, CommentReplyForm, PostSearchForm
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Max
from unidecode import unidecode
"""Метод get для передачи данных в index.html"""
class HomeView(View):
	form_class = PostSearchForm
	def get(self, request):
		posts = Post.objects.all()
		if request.GET.get('search'):
			posts = posts.filter(body__contains=request.GET['search'])
		return render(request, 'home/index.html', {'posts':posts, 'form':self.form_class}) #Передача данных

class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomments.filter(is_reply=False)  # Исправлено здесь
        user_has_liked = False
        if request.user.is_authenticated:
            user_has_liked = Vote.objects.filter(post=self.post_instance, user=request.user).exists()
        return render(request, 'home/detail.html', {
            'post': self.post_instance,
            'comments': comments,
            'form': self.form_class,
            'reply_form': self.form_class_reply,
            'user_has_liked': user_has_liked
        })

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, 'Ваш комментарий успешно отправлен', 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)



class PostDeleteView(LoginRequiredMixin, View):
	def get(self, request, post_id):
		post = get_object_or_404(Post, pk=post_id)
		if post.user.id == request.user.id:
			post.delete()
			messages.success(request, 'пост успешно удалён', 'success')
		else:
			messages.error(request, 'ты не можешь удалить этот пост', 'danger')
		return redirect('home:home')


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance
        if not post.user.id == request.user.id:
            messages.error(request, 'вы не можете обновить этот пост', 'danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', {'form':form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            base_slug = slugify(unidecode(form.cleaned_data['body'][:30]))
            slug = base_slug
            num = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            new_post.slug = slug
            new_post.save()
            messages.success(request, 'вы обновили этот пост', 'success')
            return redirect('home:post_detail', post.id, post.slug)

        return render(request, 'home/update.html', {'form': form})



class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'home/create.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            if not new_post.slug:
                base_slug = slugify(unidecode(new_post.body[:30])) or 'default-slug'
                slug = base_slug
                num = 1
                while Post.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{num}"
                    num += 1
                new_post.slug = slug
            new_post.save()
            messages.success(request, 'Вы создали новый пост', 'success')
            return redirect('home:post_detail', new_post.id, new_post.slug)

        return render(request, 'home/create.html', {'form': form})

class PostAddReplyView(LoginRequiredMixin, View):
	form_class = CommentReplyForm

	def post(self, request, post_id, comment_id):
		post = get_object_or_404(Post, id=post_id)
		comment = get_object_or_404(Comment, id=comment_id)
		form = self.form_class(request.POST)
		if form.is_valid():
			reply = form.save(commit=False)
			reply.user = request.user
			reply.post = post
			reply.reply = comment
			reply.is_reply = True
			reply.save()
			messages.success(request, 'ваш ответ успешно отправлен', 'success')
		return redirect('home:post_detail', post.id, post.slug)


class PostLikeView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        vote, created = Vote.objects.get_or_create(post=post, user=request.user)
        if created:
            post.likes_count = post.likes_count() + 1
            messages.success(request, 'Вам понравился этот пост', 'success')
        else:
            vote.delete()  # Убираем лайк
            post.likes_count = post.likes_count() - 1
            messages.success(request, 'Вы убрали лайк с этого поста', 'success')
        post.save()
        return redirect('home:post_detail', post.id, post.slug)

