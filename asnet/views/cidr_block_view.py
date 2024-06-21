from django.utils import timezone
from django.views import generic

from asnet.models import CIDRBlock


class CIDRBlockDetailView(generic.DetailView):
    """
    View to display detailed information about a CIDR block,
    with enhancements for performance, context, and user experience.
    """

    model = CIDRBlock
    template_name = "asnet/cidr_block_detail.html"
    context_object_name = "cidr_block"  # Explicitly set for clarity

    # Optimized queryset for efficiency
    def get_queryset(self):
        return CIDRBlock.objects.select_related(
            # "autonomous_system", "ip_hosts__services__vulnerabilities"
            "autonomous_system", "ip_hosts__services "
        ).prefetch_related("ip_hosts").filter(published__lte=timezone.now()).order_by("-published")


class CIDRBlockListView(generic.ListView):
    """
    View to list CIDR blocks with enhancements for performance, filtering, and user experience.
    """

    model = CIDRBlock  # Explicitly specify the model for clarity
    template_name = "asnet/cidr_block_list.html"
    context_object_name = "cidr_list"
    paginate_by = 20  # Set 20 items per page

    def get_queryset(self):
        """
        Fetches and filters CIDR blocks with advanced options.
        """
        queryset = super().get_queryset().filter(published__lte=timezone.now()).order_by("-published")

        # Apply filtering based on query parameters (example)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(cidr__icontains=query)

        # Optimize queryset for efficiency
        queryset = queryset.select_related("autonomous_system")  # Fetch related AS in a single query

        return queryset
