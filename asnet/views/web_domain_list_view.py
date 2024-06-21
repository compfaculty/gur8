from django.contrib.auth.mixins import LoginRequiredMixin  # Import for authorization
from django.db.models import Q
from django.utils import timezone
from django.views import generic

from asnet.models import WebDomain


class WebDomainListView(generic.ListView):  # Enforce login requirement
    template_name = "asnet/web_domain_list.html"
    context_object_name = "web_domains"
    paginate_by = 25  # Add pagination for better performance

    def get_queryset(self):
        base_queryset = WebDomain.objects.filter(published__lte=timezone.now()).order_by("-published")

        # Enable search functionality (optional):
        query = self.request.GET.get("q", "")
        if query:
            base_queryset = base_queryset.filter(
                Q(url__icontains=query) | Q(description__icontains=query)  # Adjust search fields as needed
            )

        return base_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")  # Pass search query to template
        return context

# from django.utils import timezone
# from django.views import generic
#
# from asnet.models import WebDomain
#
#
# class WebDomainListView(generic.ListView):
#     template_name = "asnet/web_domain_list.html"
#     context_object_name = "web_domains"
#
#     def get_queryset(self):
#         return WebDomain.objects.filter(published__lte=timezone.now()).order_by("-published")
