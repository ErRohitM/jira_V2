import django_filters

from core.models import Tasks


class TaskFilters(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr='icontains')
    priority = django_filters.CharFilter(lookup_expr='icontains')
    due_date = django_filters.DateFromToRangeFilter()
    class Meta:
        model = Tasks
        fields = ['status', 'priority', 'due_date']