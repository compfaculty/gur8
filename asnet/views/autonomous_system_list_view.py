from django.views import generic

from asnet.models import AutonomousSystem


class AutonomousSystemListView(generic.ListView):
    """
    View to list all autonomous systems with enhancements.
    """

    model = AutonomousSystem
    template_name = "asnet/autonomous_system_list.html"
    context_object_name = "asn_list"
    paginate_by = 20  # Paginate results for better performance and readability

    def get_queryset(self):
        """
        Fetches and filters autonomous systems with advanced options.
        """
        queryset = super().get_queryset().order_by("-published")

        # Apply filtering based on query parameters (example)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)

        return queryset
