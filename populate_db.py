import os
import django
from faker import Faker
import random
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Category, Event

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

def clear_previous_data():
    # Clear all data from the relevant models
    Event.objects.all().delete()
    Category.objects.all().delete()
    User.objects.all().delete()
    print("Cleared previous data from Event, Category, and User models.")

def populate_db():
    # Clear previous data before populating
    clear_previous_data()

    fake = Faker()

    # Create Categories
    category_names = [
        "Tech Fest", "Science Fair", "Music Concert", 
        "Art Exhibition", "Startup Summit", "Workshop", "Cultural Festival"
    ]
    categories = [
        Category.objects.create(
            name=name,
            description=fake.text(max_nb_chars=100),
            color=fake.hex_color()  # Random color for variety
        ) for name in category_names
    ]
    print(f"Created {len(categories)} categories.")

    # Create Organizers and Participants (Users)
    users = []
    for _ in range(30):  # Increased to 30 to ensure enough organizers and participants
        username = fake.user_name()
        # Extract first three letters of username (or less if shorter)
        first_three = username[:3] if len(username) >= 3 else username
        email = f"{first_three}9988@gomail.com"
        user = User.objects.create_user(
            username=username,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=email,
            password='password123',  # Fixed simple password for testing purposes
            last_login=timezone.make_aware(fake.date_time_this_year()),
            is_superuser=False,
            is_staff=False,
            is_active=True,
            date_joined=timezone.make_aware(fake.date_time_this_year())
        )
        users.append(user)
    print(f"Created {len(users)} users (potential organizers and participants).")

    # Assign some users as organizers (e.g., first 5 users)
    organizers = users[:5]

    # Create Events with organizers
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
            category=random.choice(categories),
            organizer=random.choice(organizers),  # Assign a random organizer
            assets=""  # Leave assets blank; default will be used if needed
        )

        # Randomly assign participants to events (excluding the organizer)
        available_participants = [u for u in users if u not in organizers or u != event.organizer]
        assigned_participants = random.sample(available_participants, k=random.randint(1, min(20, len(available_participants))))
        event.participant.set(assigned_participants)
        events.append(event)

    print(f"Created {len(events)} events.")
    print("Database populated successfully!")

if __name__ == '__main__':
    populate_db()