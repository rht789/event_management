import os
import django
from faker import Faker
import random
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Category, Event

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

def populate_db():
    fake = Faker()

    category_names = [
        "Tech Fest", "Science Fair", "Music Concert", 
        "Art Exhibition", "Startup Summit", "Workshop", "Cultural Festival"
    ]
    categories = [
        Category.objects.create(
            name=name,
            description=fake.text(max_nb_chars=100)
        ) for name in category_names
    ]
    print(f"Created {len(categories)} categories.")

    # Create Participants (Users)
    participants = [
        User.objects.create_user(
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password='password123',  # fixed simple password for testing purposes
            last_login=timezone.make_aware(fake.date_time_this_year()),
            is_superuser=False,
            is_staff=False,
            is_active=True,
            date_joined=timezone.make_aware(fake.date_time_this_year())
        ) for _ in range(25)
    ]
    print(f"Created {len(participants)} participants.")

    # Create Events with area name and city combined
    events = []
    for _ in range(15):
        city = fake.city()
        area = fake.street_name()
        location = f"{area}, {city}"

        event = Event.objects.create(
            name=fake.sentence(nb_words=3).rstrip('.'),
            description=fake.paragraph(nb_sentences=3),
            date=fake.date_between(start_date="+30d", end_date="+90d"),
            time=fake.time(),
            location=location,
            category=random.choice(categories)
        )

        # Randomly assign participants to events
        assigned_participants = random.sample(participants, k=random.randint(1, len(participants)))
        event.participant.set(assigned_participants)
        events.append(event)

    print(f"Created {len(events)} events.")
    print("Database populated successfully!")

populate_db()
