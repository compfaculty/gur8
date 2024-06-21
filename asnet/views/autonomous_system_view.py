from django.utils import timezone
from django.views import generic

from asnet.models import AutonomousSystem


class AutonomousSystemDetailView(generic.DetailView):
    """
    View to display detailed information about an autonomous system,
    with enhancements for performance, context, and user experience.
    """

    model = AutonomousSystem
    template_name = "asnet/autonomous_system_detail.html"
    context_object_name = "autonomous_system"  # Explicitly set for clarity

    # Optimized queryset for efficiency
    def get_queryset(self):
        return AutonomousSystem.objects.select_related("cidr_blocks").prefetch_related("services").filter(
            published__lte=timezone.now()
        ).order_by("-published")