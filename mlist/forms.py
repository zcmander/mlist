import datetime

from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, HTML
from crispy_forms.bootstrap import FormActions, FieldWithButtons, PrependedText, TabHolder, Tab
from haystack.forms import SearchForm

from .models import MovieInCollection, Collection


class BetterDateTimeInput(forms.DateTimeInput):
    input_type = 'datetime'

    def __init__(self, *args, **kwargs):
        forms.DateTimeInput.__init__(self, *args, **kwargs)


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.layout = Layout(
                'title',
                FormActions(
                    Submit("submit", "Create")
                )
            )


class MovieForm(forms.ModelForm):
    class Meta:
        model = MovieInCollection
        fields = ['title', 'date', 'tags', 'collection']

    title = forms.CharField()
    jstags = forms.CharField(label="Tags", required=False)
    imdb_id = forms.CharField(required=False)
    date = forms.DateTimeField(initial=datetime.datetime.now, widget=BetterDateTimeInput)

    def __init__(self, request, *args, **kwargs):
        super(MovieForm, self).__init__(*args, **kwargs)

        self.fields["collection"].queryset = Collection.objects.filter(user=request.user)

        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.help_text_inline = True
        self.helper.attrs['autocomplete'] = 'off'
        self.helper.html5_required = True
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic',
                    Field('title', css_class="input-xlarge movie-title-typeahead"),
                    PrependedText('date', '<i class="icon-calendar"></i>', css_class="input-medium"),
                    Field('tags', type="hidden"),
                    Field('jstags', css_class="input-small tagManager", placeholder="Tag"),
                ),
                Tab('Advanced',
                    Field('collection', css_class="input-medium"),
                    Field('imdb_id', css_class="movie-imdb_id-typeahead input-small"),
                ),
            ),
            FormActions(
                Submit("submit", "Add")
            )
        )


class MovieEditForm(MovieForm):
    def __init__(self, *args, **kwargs):
        super(MovieEditForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance']
        self.fields['title'].initial = instance.movie.title
        self.fields['imdb_id'].initial = instance.movie.imdb_id
        self.fields['date'].initial = instance.date
        self.fields['jstags'].initial = ",".join([x.name for x in instance.tags.all()])

        side_effect_title = "These affects to all movie items."
        side_effect_message = "If movie IMDB ID or title is modified then all related 'watch dates' or related collections are also changed."

        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Movie item',
                    PrependedText('date', '<i class="icon-calendar"></i>', css_class="input-medium"),
                    Field('collection', css_class="input-medium"),
                    Field('tags', type="hidden"),
                    Field('jstags', css_class="input-small tagManager", placeholder="Tag"),
                ),
                Tab(
                    'Movie',
                    HTML('<div class="alert alert-warning alert-block"><strong>' + side_effect_title + '</strong><p>' + side_effect_message + '</p></div>'),
                    Field('title', css_class="input-xlarge movie-title-typeahead"),
                    Field('imdb_id', css_class="movie-imdb_id-typeahead input-small"),
                )
            ),
            FormActions(
                Submit("submit", "Save"),
                HTML('<a class="btn" href="' + reverse('detail-movie', args=(instance.id,)) + '">Cancel</a>')
            )
        )


class ImportForm(forms.Form):
    class Meta:
        layout = (
            Fieldset("Import movies from CVS", 'data'),
        )
    data = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.layout = Layout(
            Fieldset(
                'Import',
                'data',
                FormActions(
                    Submit("submit", "Import")
                )
            )
        )


class MovieSearchForm(SearchForm):
    def __init__(self, *args, **kwargs):
        super(MovieSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "get"
        self.helper.form_class = "form-horizontal form-search"
        self.helper.layout = Layout(
                    FieldWithButtons(Field('q', css_class="search-query"), Submit("submit", "Search"), css_class="input-search"),
            )
