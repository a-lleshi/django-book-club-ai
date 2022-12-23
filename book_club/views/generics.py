from django.views.generic import ListView


class FilteredListView(ListView):
    """Returns a list of objects filtered by keywords"""
    filterset_class = None

    def get_queryset(self, new_qs=None):
        qs = new_qs if new_qs is not None else super().get_queryset()
        self.filterqs = self.filterset_class(self.request.GET, queryset=qs)
        return self.filterqs.qs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['filter'] = self.filterqs
        return context_data
