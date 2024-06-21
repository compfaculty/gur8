from django.db.models import Q
from django.utils import timezone
from django.views import generic

from asnet.models import IpHost


class IpHostListView(generic.ListView):
    """
    View to list IP hosts with enhancements for performance, filtering, sorting, and user experience.
    """

    model = IpHost  # Explicitly specify the model for clarity
    template_name = "asnet/ip_host_list.html"
    context_object_name = "ip_hosts"
    paginate_by = 25  # Set 25 items per page for efficient pagination

    def get_queryset(self):
        """
        Fetches and filters IP hosts with advanced options.
        """
        queryset = super().get_queryset().filter(published__lte=timezone.now()).order_by("-published")

        # Apply filtering based on query parameters (example)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(ip__icontains=query) | Q(name__icontains=query))  # Search by IP or name

        # Apply sorting based on query parameters (example)
        sort_by = self.request.GET.get("sort_by")
        if sort_by == "ip":
            queryset = queryset.order_by("ip")
        elif sort_by == "name":
            queryset = queryset.order_by("name")

        # Optimize queryset for efficiency
        queryset = queryset.select_related("cidr_block")  # Fetch related CIDR block in a single query

        return queryset



