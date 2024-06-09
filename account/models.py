from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Relation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} following {self.to_user}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField(default=0, verbose_name='Возраст')
    bio = models.TextField(null=True, blank=True, verbose_name='О себе')



class Thread(models.Model):
    # Поле для связи "многие ко многим" с пользователями
    users = models.ManyToManyField(User)

    def __str__(self):
        # Метод возвращает строковое представление объекта Thread, перечисляя всех пользователей, участвующих в чате
        return f'Thread between {", ".join(user.username for user in self.users.all())}'

    def add_users(self, user1, user2):
        # Метод для добавления двух пользователей в чат
        self.users.add(user1)
        self.users.add(user2)


class Message(models.Model):
    # Поле для связи "один ко многим" с моделью Thread
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    # Поле для связи "один ко многим" с отправителем сообщения
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    # Поле для связи "один ко многим" с получателем сообщения
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    # Текст сообщения
    content = models.TextField(verbose_name='Сообщение')
    # Дата и время создания сообщения
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Метод возвращает строковое представление объекта Message, показывая отправителя и первые 30 символов сообщения
        return f'{self.sender.username}: {self.content[:30]}'




