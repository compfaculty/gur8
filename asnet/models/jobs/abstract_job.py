from django.db import models


class AbstractJob(models.Model):
    """
    Abstract base class for representing a job that can be processed asynchronously.

    Defines common fields and behavior for jobs, such as status tracking and error handling.
    """

    # Job status constants
    STATUS_PENDING = "pending"  # Job is waiting to be processed
    STATUS_RUNNING = "running"  # Job is currently being processed
    STATUS_DONE = "done"        # Job has completed successfully
    STATUS_FAILED = "failed"    # Job has encountered an error

    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_RUNNING, "Running"),
        (STATUS_DONE, "Done"),
        (STATUS_FAILED, "Failed"),
    )

    status = models.CharField(
        max_length=7,
        choices=STATUSES,
        default=STATUS_PENDING,
        help_text="The current status of the job",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the job was first created",
    )

    error_message = models.CharField(
        max_length=512,
        default="",
        help_text="An error message if the job failed",
    )

    def process(self):
        """
        Processes the job.

        This method should be implemented by subclasses to perform the actual job logic.
        """
        raise NotImplementedError("Subclasses must implement the 'process' method")

    class Meta:
        abstract = True  # This model cannot be directly instantiated
