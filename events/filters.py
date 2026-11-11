import django_filters
from django.core.exceptions import ValidationError
from .models import Event
from django import forms

class EventFilterForm(forms.Form):
    def clean(self):
        clean_data = super().clean()

        min_price = clean_data.get('min_price')
        max_price = clean_data.get('max_price')

        if min_price is not None and max_price is not None and min_price > max_price:
            self.add_error('max_price', 'min_price can not be greater than max_price')

        return clean_data

class EventFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name = 'title',
        lookup_expr = 'icontains'
    )
    min_price = django_filters.NumberFilter(
        method = 'ignore_price_filter',
    )
    max_price = django_filters.NumberFilter(
        method = 'ignore_price_filter'
    )

    ordering = django_filters.OrderingFilter(
        fields = (
            ('event_date', 'event_date'),
            ('title', 'title'),

        )
    )

    class Meta:
        model = Event
        fields = {
            'location': ['exact', 'icontains'],
            'status': ['exact'],
            'event_date': ['exact', 'gte', 'lte'],
        }
        form = EventFilterForm

    def ignore_price_filter(self, queryset, name, value):
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        min_price = self.form.cleaned_data.get('min_price')
        max_price = self.form.cleaned_data.get('max_price')

        if min_price is not None and max_price is not None:
            queryset = queryset.filter(
                ticket_types__price__gte = min_price,
                ticket_types__price__lte = max_price
            ).distinct()

        if min_price is not None and max_price is not None:
            queryset = queryset.filter(
                ticket_types__price__gte=min_price,
                ticket_types__price__lte=max_price
            ).distinct()

        elif min_price is not None:
            queryset = queryset.filter(
                ticket_types__price__gte=min_price
            ).distinct()

        elif max_price is not None:
            queryset = queryset.filter(
                ticket_types__price__lte=max_price
            ).distinct()

        if not self.form.cleaned_data.get('ordering'):
            queryset = queryset.order_by('event_date')

        return queryset