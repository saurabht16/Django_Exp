from django.contrib import admin
from django import forms
from django.forms import ModelForm

from .models import Choice, Question, MyChoice
from nested_inline.admin import NestedTabularInline, NestedModelAdmin


class LevelTwoInline(NestedTabularInline):
    model = MyChoice
    extra = 0
    fk_name = 'choice'
    readonly_fields = ('mychoice_text', 'myvotes')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ChoiceInline(NestedTabularInline):
    model = Choice
    extra = 0
    readonly_fields = ('choice_text', 'votes')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    inlines = [LevelTwoInline]


    class Media:
        css = {"all": ("css/hide_admin_original.css",)}


class Segmentation_Form(ModelForm):
    year_in_school = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=Question.YEAR_IN_SCHOOL_CHOICES)


class QuestionAdmin(NestedModelAdmin):
    form = Segmentation_Form
    fieldsets = [
        (None,               {'fields': ['question_text', 'year_in_school']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    readonly_fields = ('question_text',)

    class Media:
        css = {"all": ("css/hide_admin_original.css",)}

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Question, QuestionAdmin)
# Register your models here.
