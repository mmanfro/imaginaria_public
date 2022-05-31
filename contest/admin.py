from django.contrib import admin

from contest.models import Contest, Participant


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):

    filter_horizontal = ("judges",)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.save()


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.save()
