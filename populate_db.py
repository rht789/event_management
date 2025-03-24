import os
import django
from faker import Faker
import random
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import Group
from events.models import Category, Event

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

# Get the custom User model
User = get_user_model()

def clear_previous_data():
    # Clear only Event and Category data, preserve Users and Groups
    Event.objects.all().delete()
    Category.objects.all().delete()
    print("Cleared previous data from Event and Category models (preserved Users and Groups).")

def populate_db():
    # Clear previous data (only Events and Categories)
    clear_previous_data()

    fake = Faker()

    # Check for existing groups; create if they don't exist
    group_names = ["Admin", "Organizer", "Participant"]
    groups = {}
    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)
        groups[name] = group
        if created:
            print(f"Created group: {name}")
    print(f"Ensured {len(groups)} groups exist: {', '.join(group_names)}.")

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

    # Get existing users
    users = list(User.objects.all())
    print(f"Found {len(users)} existing users.")

    # Create additional users if needed (to ensure at least 30 users for variety)
    target_user_count = 30
    if len(users) < target_user_count:
        for _ in range(target_user_count - len(users)):
            username = fake.user_name()
            # Ensure username is unique
            while User.objects.filter(username=username).exists():
                username = fake.user_name()
            first_three = username[:3] if len(username) >= 3 else username
            email = f"{first_three}9988@gomail.com"
            # Ensure email is unique
            while User.objects.filter(email=email).exists():
                first_three = fake.user_name()[:3]
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
                date_joined=timezone.make_aware(fake.date_time_this_year()),
                phone=fake.phone_number()[:15],  # Limit phone number length to 15 characters
                location=f"{fake.city()}, {fake.country()}",
                bio=fake.paragraph(nb_sentences=2),
                profile_image=None  # Set to None; can be updated later if needed
            )
            # Assign a random role to the new user
            role = random.choice(list(groups.values()))
            user.groups.add(role)
            users.append(user)
        print(f"Created {target_user_count - len(users)} additional users to reach {target_user_count} total users.")
    else:
        print("Enough users already exist; no new users created.")

    # Assign some users as organizers (e.g., users with "Organizer" role)
    organizers = [user for user in users if user.groups.filter(name="Organizer").exists()]
    if not organizers:
        # Ensure at least one organizer exists
        user = random.choice(users)
        user.groups.clear()
        user.groups.add(groups["Organizer"])
        organizers.append(user)
    print(f"Assigned {len(organizers)} users as organizers.")

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
        available_participants = [u for u in users if u != event.organizer]
        assigned_participants = random.sample(available_participants, k=random.randint(1, min(20, len(available_participants))))
        event.participant.set(assigned_participants)
        events.append(event)

    print(f"Created {len(events)} events.")
    print("Database populated successfully!")

if __name__ == '__main__':
    populate_db()