from client.models import Campaign, campaign_allocation, CampaignTrack
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from client.utils import percentage
from vendors.utils import *
@receiver(post_save, sender=Campaign)
def campaign_change(sender, instance, created, **kwargs):
    if created:
        track = CampaignTrack.objects.create(campaign=instance, created_date=datetime.now(), start_date=instance.start_date)
        track.save()

@receiver(post_save, sender=campaign_allocation)
def cam_alloc_change(sender, instance, created, **kwargs):

    if CampaignTrack.objects.filter(campaign_id=instance.campaign_id).exists():
        track = CampaignTrack.objects.get(campaign_id=instance.campaign_id)
        camp_all = campaign_allocation.objects.get(id=instance.id)
        if instance.status == 5:
            if track.data_vendor_assign_count > 0:
                list = eval(track.data_vendor_assign)
                if any(d['camp_alloc_id'] == instance.id for d in list) != True:
                    print('hello')
                    d = {}
                    d['type'] = 'vendor'
                    d['vendor_id'] = instance.client_vendor.id
                    d['Name'] = instance.client_vendor.user_name
                    t = datetime.now()
                    d['date'] = t.isoformat()
                    d['camp_alloc_id'] = instance.id
                    d['assigned_leads'] = instance.volume
                    d['cpl'] = instance.cpl
                    d['vendor_percentage'] = vendorper(camp_all.id)
                    d['client_percentage'] = percentage(instance.campaign_id)
                    # d['percentage'] = percentage(instance.campaign_id)
                    list.append(d)
                    track.data_vendor_assign = list
                    track.data_vendor_assign_count += 1
                    track.save()
            else:
                L = []
                d = {}
                d['type'] = 'vendor'
                d['vendor_id'] = instance.client_vendor.id
                d['Name'] = instance.client_vendor.user_name
                t = datetime.now()
                d['date'] = t.isoformat()
                d['camp_alloc_id'] = instance.id
                d['assigned_leads'] = instance.volume
                d['cpl'] = instance.cpl
                d['vendor_percentage'] = vendorper(camp_all.id)
                d['client_percentage'] = percentage(instance.campaign_id)
                L.append(d)
                track.data_vendor_assign = L
                track.data_vendor_assign_count += 1
                track.save()
