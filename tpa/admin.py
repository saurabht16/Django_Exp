from django.contrib import admin
from django import forms
from .utils import OptionalChoiceField
from django.forms import ModelForm
import floppyforms
from .models import Choice, Question, MyChoice, newChoice
from nested_inline.admin import NestedTabularInline, NestedModelAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .fields import ListTextWidget
from simple_history.admin import SimpleHistoryAdmin
from reversion.admin import VersionAdmin
from import_export import fields
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from import_export.widgets import ForeignKeyWidget
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.http import HttpResponseForbidden
from import_export.forms import ConfirmImportForm
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from import_export.results import RowResult
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import pluralize
from django.contrib import messages
from import_export.signals import post_export, post_import

class ChoiceResource(resources.ModelResource):
    question_txt = fields.Field(
        column_name='question',
        attribute='question',
        widget=ForeignKeyWidget(Question, 'question_text'))
    newchoice_txt = fields.Field(
        column_name='newchoice',
        attribute='newchoice',
        widget=ForeignKeyWidget(newChoice, 'newquestion'))

    class Meta:
        model = Choice
        fields = ('id','choice_text' ,'votes', 'question_txt', 'newchoice_txt')
        export_order = ('id', 'choice_text' ,'votes', 'question_txt', 'newchoice_txt')


from dal import autocomplete

from django import forms


class newChoiceForm(forms.ModelForm):
    class Media:
        js = ('js/number-polyfill.js',)
    Choices = (
        ('FRESHMAN', 'Freshman'),
        ('SOPHOMORE', 'Sophomore'),
        ('JUNIOR', 'Junior'),
        ('SENIOR', 'Senior'),
    )
    choice_text = forms.ChoiceField(choices=Choices)
    widgets = {
        'votes': forms.TextInput(attrs={'step': 1}),
    }
    b = newChoice.objects.select_related()

    print(b)
    newchoice = forms.ModelChoiceField(
         queryset=b,
         widget=autocomplete.ModelSelect2(url='newchoice-autocomplete', forward=('mychoice', 'newchoice', ))
     )

    class Meta:
        model = Choice
        fields = ('__all__')


from django.contrib.admin.views.main import ChangeList
from django.core.paginator import EmptyPage, InvalidPage, Paginator


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__['get_query_string']

    def __init__(self, request, page_num, paginator):
        self.show_all = 'all' in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())


class PaginationInline(admin.TabularInline):
    template = 'admin/edit_inline/tabular_paginated.html'
    per_page = 20
    print("********************%%%%%%%%%%%%%%%%%%%%%%%%%%**")

    def get_formset(self, request, obj=None, **kwargs):
            formset_class = super(PaginationInline, self).get_formset(
                request, obj, **kwargs)

            class PaginationFormSet(formset_class):
                def __init__(self, *args, **kwargs):
                    super(PaginationFormSet, self).__init__(*args, **kwargs)

                    qs = self.queryset
                    paginator = Paginator(qs, self.per_page)
                    try:
                        page_num = int(request.GET.get('p', '0'))
                    except ValueError:
                        page_num = 0

                    try:
                        page = paginator.page(page_num + 1)
                    except (EmptyPage, InvalidPage):
                        page = paginator.page(paginator.num_pages)

                    self.cl = InlineChangeList(request, page_num, paginator)
                    self.paginator = paginator

                    if self.cl.show_all:
                        self._queryset = qs
                    else:
                        self._queryset = page.object_list

            PaginationFormSet.per_page = self.per_page
            return PaginationFormSet

class ChoiceInline(PaginationInline):
    model = Choice
    form = newChoiceForm
    extra = 0
    #resource_class = ChoiceResource
    #classes = ['collapse']
    #readonly_fields = ('choice_text', 'votes')

    #template = 'admin/edit_inline/tabular_paginated.html'


class ChoiceAdmin(ImportExportModelAdmin):
    resource_class = ChoiceResource
    def get_model_perms(self, request):
         """
         Return empty perms dict thus hiding the model from admin index.
         """
         return {}

    def process_import(self, request, *args, **kwargs):
        '''
        Perform the actual import action (after the user has confirmed he
        wishes to import)
        '''
        opts = self.model._meta
        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))
        print(kwargs)
        id = kwargs["id"]
        print("aaaaaa")
        confirm_form = ConfirmImportForm(request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            tmp_storage = self.get_tmp_storage_class()(name=confirm_form.cleaned_data['import_file_name'])
            data = tmp_storage.read(input_format.get_read_mode())
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            result = resource.import_data(dataset, dry_run=False,
                                          raise_errors=True,
                                          file_name=confirm_form.cleaned_data['original_file_name'],
                                          user=request.user)

            if not self.get_skip_admin_log():
                # Add imported objects to LogEntry
                logentry_map = {
                    RowResult.IMPORT_TYPE_NEW: ADDITION,
                    RowResult.IMPORT_TYPE_UPDATE: CHANGE,
                    RowResult.IMPORT_TYPE_DELETE: DELETION,
                }
                content_type_id = ContentType.objects.get_for_model(self.model).pk
                for row in result:
                    if row.import_type != row.IMPORT_TYPE_ERROR and row.import_type != row.IMPORT_TYPE_SKIP:
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=content_type_id,
                            object_id=row.object_id,
                            object_repr=row.object_repr,
                            action_flag=logentry_map[row.import_type],
                            change_message="%s through import_export" % row.import_type,
                        )

            success_message = u'Import finished, with {} new {}{} and ' \
                              u'{} updated {}{}.'.format(result.totals[RowResult.IMPORT_TYPE_NEW],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_NEW]),
                                                         result.totals[RowResult.IMPORT_TYPE_UPDATE],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_UPDATE]))

            messages.success(request, success_message)
            tmp_storage.remove()

            post_import.send(sender=None, model=self.model)

        url = reverse('admin:%s_%s_change' % ('tpa', 'mychoice'), args=(id),
                      current_app=self.admin_site.name)
        return HttpResponseRedirect(url)

    def changelist_view(self, request, extra_context=None):
        return HttpResponseForbidden()

    def change_view(self, request, extra_context=None):
        return HttpResponseForbidden()

    def add_view(self, request, extra_context=None):
        return HttpResponseForbidden()

    def history_view(self, request, extra_context=None):
        return HttpResponseForbidden()


admin.site.register(Choice, ChoiceAdmin)


class Segmentation_Form(ModelForm):
    mychoice = forms.ModelChoiceField(
        queryset=MyChoice.objects.all(),
    )

    class Media:
        js = ('js/number-polyfill.js',)
        #year_in_school = floppyforms.CharField(widget=floppyforms.TextInput(
    #    datalist=['A', 'B', 'C'],
    #    attrs={'autocomplete': 'off'})
    #)
    #year_in_school = OptionalChoiceField(choices=(("", "-----"), ("1", "1"), ("2", "2")))
    #year_in_school = forms.ChoiceField( choices=Question.YEAR_IN_SCHOOL_CHOICES)
    year_in_school = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        _country_list = kwargs.pop('data_list', None)
        super(Segmentation_Form, self).__init__(*args, **kwargs)

        # the "name" parameter will allow you to use the same widget more than once in the same
        # form, not setting this parameter differently will cuse all inputs display the
        # same list.
        country_list = ('Mexico', 'USA', 'China', 'France')
        self.fields['year_in_school'].widget = ListTextWidget(data_list=country_list, name='country-list')
    print("*****************************************")


class QuestionAdmin(ImportExportModelAdmin, VersionAdmin):


    form = Segmentation_Form
    fieldsets = [
        (None,               {'fields': ['question_text', 'mychoice', 'year_in_school']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
   # resource_class = ChoiceResource
    #readonly_fields = ('question_text',)

    class Media:
        css = {"all": ("css/hide_admin_original.css",)}

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_generate_meta'] = True
        return super(QuestionAdmin, self).change_view(request, object_id,
                                                     form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if '_meta' in request.POST.keys():
            from django.contrib import messages
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Error Validating The Mappings ..')
            obj.is_draft = True
            pass

        # Let Django do its defaults.
        super(QuestionAdmin, self).save_model(request, obj, form, change)

admin.site.register(Question, QuestionAdmin)
# Register your models here.


class newChoiceAdmin(admin.ModelAdmin):
    fieldsets = [
    (None, {'fields': ['newquestion', 'question', 'votes']}),

]
admin.site.register(newChoice, newChoiceAdmin)

class MyChoiceAdmin(ImportExportModelAdmin):
    fieldsets = [
    (None, {'fields': ['mychoice_text', 'myvotes']}),
]


admin.site.register(MyChoice, MyChoiceAdmin)