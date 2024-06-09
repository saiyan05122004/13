from django.contrib import admin
from .models import Relation, Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class ProfileInline(admin.StackedInline):
	model = Profile
	can_delete = False


class ExtendedUserAdmin(UserAdmin):
	inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Relation)

from django.contrib import admin
from .models import Thread

admin.site.register(Thread)


from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'content', 'created']  # Включите 'recipient' в список отображения
    list_filter = ['sender', 'recipient', 'created']  # Включите 'recipient' в список фильтров
    search_fields = ['sender__username', 'recipient__username', 'content']  # Добавьте поиск по 'recipient'

admin.site.register(Message, MessageAdmin)
