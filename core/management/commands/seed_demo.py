from django.core.management.base import BaseCommand
from members.models import Member, Skill
from events.models import Event
from roster.models import DutyPosition, DutyAssignment
from equipment.models import EquipmentCategory, Equipment
from core.models import Announcement
from datetime import date, time, timedelta

class Command(BaseCommand):
    help = "Create a small demo dataset."
    def handle(self, *args, **kwargs):
        skills = {}
        for name in ["Camera", "Photography", "Sound", "Streaming", "Projection", "Lighting"]:
            skills[name], _ = Skill.objects.get_or_create(name=name)
        people = [
            ("Brian", "Camera Operator", ["Camera","Streaming"]),
            ("John", "Camera Operator", ["Camera"]),
            ("Mary", "Photographer", ["Photography"]),
            ("David", "Sound Engineer", ["Sound"]),
            ("James", "Projection", ["Projection"]),
            ("Peter", "Lighting", ["Lighting"]),
        ]
        members = []
        for name, role, skill_names in people:
            m, _ = Member.objects.get_or_create(name=name, defaults={"role": role})
            m.role = role; m.is_active = True; m.save()
            m.skills.set([skills[s] for s in skill_names])
            members.append(m)

        event, _ = Event.objects.get_or_create(
            name="Sunday Service",
            date=date.today() + timedelta(days=(6-date.today().weekday()) % 7),
            defaults={"event_type":"service","start_time":time(9,0),"call_time":time(7,30),"location":"Main Sanctuary"}
        )
        positions = {}
        for name in ["Camera 1","Camera 2","Photography","Sound","Projection","Lighting"]:
            positions[name], _ = DutyPosition.objects.get_or_create(name=name)
        for pos_name, member in zip(positions, members):
            DutyAssignment.objects.get_or_create(event=event, position=positions[pos_name], defaults={"member":member})
        cat, _ = EquipmentCategory.objects.get_or_create(name="Cameras")
        Equipment.objects.get_or_create(equipment_id="CAM-001", defaults={"name":"Main Camera","category":cat,"brand":"Demo","model":"Camera X","condition":"good","location":"Media Store"})
        Announcement.objects.get_or_create(title="Welcome to the Media System", defaults={"message":"Demo data has been created. Replace it with your church's real information.","priority":"normal","published":True})
        self.stdout.write(self.style.SUCCESS("Demo data created."))
