from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from .forms import (
    UserRegistrationForm, UserLoginForm, EditUserForm, MessageForm
)
from .models import Relation, Thread

# User Account Views

class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'вы успешно зарегистрировались', 'success')
            return redirect('home:home')
        return render(request, self.template_name, {'form': form})

class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'вы успешно вошли в систему', 'success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, 'имя пользователя или пароль неверны', 'warning')
        return render(request, self.template_name, {'form': form})

class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'вы успешно вышли из системы', 'success')
        return redirect('home:home')

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        is_following = relation.exists()

        # Получаем или создаем чат между текущим пользователем и просматриваемым пользователем
        thread = Thread.objects.filter(users=user).filter(users=request.user).first()
        if not thread:
            thread = Thread.objects.create()
            thread.users.add(request.user, user)

        # Проверяем, является ли текущий пользователь профилем, который просматривается
        is_own_profile = request.user == user

        context = {
            'user': user,
            'posts': posts,
            'is_following': is_following,
            'is_own_profile': is_own_profile,
            'thread': thread,
            'user_id': user_id,
        }
        # Передаем контекст и данные в шаблон для отображения профиля пользователя
        return render(request, 'account/profile.html', context)

class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/password_reset_form.html'
    success_url = reverse_lazy('account:password_reset_done')
    email_template_name = 'account/password_reset_email.html'

class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'

class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/password_reset_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')

class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'

class UserFollowView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['user_id'])
        if user.id != request.user.id:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'вы не можете подписаться на свой аккаунт или отписаться от него', 'danger')
            return redirect('account:user_profile', user.id)

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.error(request, 'вы уже подписаны на этого пользователя', 'danger')
        else:
            Relation(from_user=request.user, to_user=user).save()
            messages.success(request, 'вы подписались на этого пользователя', 'success')
        return redirect('account:user_profile', user.id)

class UserUnfollowView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs['user_id'])
        if user.id != request.user.id:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, 'вы не можете подписаться на свой аккаунт или отписаться от него', 'danger')
            return redirect('account:user_profile', user.id)

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request, 'вы отписались от этого пользователя', 'success')
        else:
            messages.error(request, 'вы не подписаны на этого пользователя', 'danger')
        return redirect('account:user_profile', user.id)

class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserForm

    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={'email': request.user.email})
        return render(request, 'account/edit_profile.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'профиль успешно отредактирован', 'success')
        return redirect('account:user_profile', request.user.id)

# Чат

class SendMessageToUserView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        # Получаем получателя сообщения по его id или выдаем ошибку 404, если пользователь не существует
        recipient = get_object_or_404(User, id=user_id)
        # Проверяем наличие существующего чата между текущим пользователем и получателем
        thread = Thread.objects.filter(users=request.user).filter(users=recipient).first()
        if thread is not None:
            # Если чат уже существует, отправляем пользователя на страницу деталей чата
            return redirect('account:thread_detail', pk=thread.pk)
        # Если чат не существует, создаем форму для отправки сообщения
        form = MessageForm()
        return render(request, 'account/send_message.html', {'recipient': recipient, 'form': form})

    def post(self, request, user_id):
        recipient = get_object_or_404(User, id=user_id)
        # Проверяем наличие существующего чата между текущим пользователем и получателем
        thread = Thread.objects.filter(users=request.user).filter(users=recipient).first()
        if thread is None:
            # Если чат не существует, создаем новый и добавляем участников
            thread = Thread.objects.create()
            thread.users.add(request.user, recipient)

        form = MessageForm(request.POST)
        if form.is_valid():
            # Создаем сообщение и связываем его с чатом, отправителем и получателем
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.recipient = recipient
            message.save()
            return redirect('account:thread_detail', pk=thread.pk)

        return render(request, 'account/send_message.html', {'recipient': recipient, 'form': form})

class ThreadDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        thread = get_object_or_404(Thread, id=pk)
        # Проверяем, участвует ли текущий пользователь в данном чате
        if request.user not in thread.users.all():
            # Если нет, создаем новый чат и добавляем текущего пользователя и другого участника
            new_thread = Thread.objects.create()
            new_thread.users.add(request.user)
            new_thread.users.add(thread.users.first())
            return redirect('account:thread_detail', pk=new_thread.pk)
        
        messages = thread.messages.all()
        form = MessageForm()
        other_user = thread.users.exclude(id=request.user.id).first()
        return render(request, 'account/thread_detail.html', {'thread': thread, 'messages': messages, 'form': form, 'other_user': other_user})

    def post(self, request, pk):
        thread = get_object_or_404(Thread, id=pk)
        if request.user not in thread.users.all():
            # Если текущий пользователь не участвует в чате, создаем новый и добавляем участников
            new_thread = Thread.objects.create()
            new_thread.users.add(request.user)
            new_thread.users.add(thread.users.first())
            thread = new_thread

        form = MessageForm(request.POST)
        if form.is_valid():
            # Создаем сообщение и связываем его с чатом, отправителем и получателем
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.recipient = thread.users.exclude(id=request.user.id).first()
            message.save()
            return redirect('account:thread_detail', pk=thread.pk)
        
        messages = thread.messages.all()
        other_user = thread.users.exclude(id=request.user.id).first()
        return render(request, 'account/thread_detail.html', {'thread': thread, 'messages': messages, 'form': form, 'other_user': other_user})


class ThreadDeleteView(LoginRequiredMixin, DeleteView):
    model = Thread
    template_name = 'account/thread_confirm_delete.html'
    success_url = reverse_lazy('account:thread_list')

    def get_queryset(self):
        # Возвращаем только чаты, в которых участвует текущий пользователь
        queryset = super().get_queryset()
        return queryset.filter(users=self.request.user)


class ThreadListView(View):
    def get(self, request):
        # Получаем все чаты, в которых участвует текущий пользователь
        threads = Thread.objects.filter(users=request.user)
        # Создаем список данных о чатах для передачи в шаблон
        thread_data = [
            {'thread': thread, 'other_user': thread.users.exclude(id=request.user.id).first()}
            for thread in threads
        ]
        return render(request, 'account/thread_list.html', {'thread_data': thread_data})
