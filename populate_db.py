import os
import django
from faker import Faker
import random
from events.models import Category, Participant, Event

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

def populate_db():
    fake = Faker()

    # Create Categories
    categories = [Category.objects.create(
        name=fake.word().capitalize(),
        description=fake.text()
    ) for _ in range(7)]
    print(f"Created {len(categories)} categories.")

    # Create Participants
    participants = [Participant.objects.create(
        name=fake.name(),
        email=fake.unique.email()
    ) for _ in range(15)]
    print(f"Created {len(participants)} participants.")

    # Create Events
    events = []
    for _ in range(15):
        event = Event.objects.create(
            name=fake.sentence(nb_words=3).replace('.', ''),
            description=fake.paragraph(),
            date=fake.date_between(start_date="+30d", end_date="+90d"),
            time=fake.time(),
            location=fake.city(),
            category=random.choice(categories)
        )
        event.participant.set(random.sample(participants, k=random.randint(1, len(participants))))
        events.append(event)
    print(f"Created {len(events)} events.")

    print("Database populated successfully!")

populate_db()
