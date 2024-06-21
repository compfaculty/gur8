import importlib
import logging

import dramatiq

# from services import ping_cidr
# from utils import asn_to_cidr_blocks


logger = logging.getLogger(__name__)
models = importlib.import_module("asnet.models")


@dramatiq.actor
def create_cidr_blocks_for_asn(pk, asn):
    pass
    # cidr_block_model = getattr(models, "CIDRBlock")
    # cidr_blocks = asn_to_cidr_blocks(asn)
    # if cidr_blocks:
    #     for cidr in cidr_blocks:
    #         try:
    #             cidr_block, created = cidr_block_model.objects.get_or_create(cidr=cidr,
    #                                                                          defaults={'autonomous_system_id': pk})
    #             if created:
    #                 # Object was created
    #                 create_cidr_blocks_for_asn.logger.info("CIDRBlock created with CIDR:", cidr)
    #             else:
    #                 # Object already existed
    #                 create_cidr_blocks_for_asn.logger.warning("CIDRBlock already exists with CIDR:", cidr)
    #         except Exception as e:
    #             create_cidr_blocks_for_asn.logger.error("An error occurred:", e)


@dramatiq.actor
def create_ip_hosts_for_cidr(pk, cidr):
    pass
    # ip_host_model = getattr(models, "IpHost")
    # ips = ping_cidr(cidr)
    # if ips:
    #     for ip in ips:
    #         ip_host_model.objects.create(ip=ip, cidr=pk)


@dramatiq.actor(max_retries=3, time_limit=86_400_000)
def process_job(instance_id, instance_type):
    # TODO add delete old tasks
    from django_dramatiq.tasks import delete_old_tasks
    delete_old_tasks.send(max_task_age=60 * 60)

    Job = getattr(models, "AbstractJob")
    model = getattr(models, instance_type)
    job = model.objects.get(pk=instance_id)
    try:
        if job:
            job.status = Job.STATUS_RUNNING
            job.save()
            job.process()
            job.status = Job.STATUS_DONE
            job.save()
    except Exception as ex:
        process_job.logger.error(f"job failed. An error occurred: {ex}", ex)
        if job:
            job.status = Job.STATUS_FAILED
            job.error_message = f"error: {ex}"
            job.save()
