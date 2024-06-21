from django.utils import timezone
from django.views import generic

from asnet.models import AutonomousSystem


class IndexView(generic.ListView):
    template_name = "asnet/index.html"
    context_object_name = "asn_list"

    def get_queryset(self):
        return AutonomousSystem.objects.filter(published__lte=timezone.now()).order_by("-published")[:25]
