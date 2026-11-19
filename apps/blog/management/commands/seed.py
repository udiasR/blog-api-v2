from django.core.management import BaseCommand, CommandParser, CommandError
from typing import Any
from django.db import transaction
from faker import Faker
from apps.blog.models import Comment, Tag, Post, Category
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password


EMAIL_DOMAIN = "example.com"
SEED_PASSWORD = "lorem ipsum"

User = get_user_model()

class Command(BaseCommand):
    help = "Fill the database with fake data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users",
            default = 20,
            type = int,
            help = "Number of users to create",
        )

        parser.add_argument(
            "--posts",
            default = 100,
            type=int,
            help="Number of posts to create",
        )

        parser.add_argument(
            "--comments",
            default=500,
            type=int,
            help="Number of comments to create",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data before seeding"
        )


    def handle(self, *args: Any, **options: Any) ->None:
        users_count: int = options["users"]
        posts_count: int = options["posts"]
        comments_count: int = options["comments"]
        clear: bool = options["clear"]

        for name, value in (("--users", users_count), ("--posts", posts_count), ("--comments", comments_count)):
            if value < 0:
                raise CommandError(f"{name} cannot be less than 0")

        fake = Faker("kk_KZ")


        with transaction.atomic():
            if options["clear"]:
                self.__clear()
            if (posts_count or comments_count) and User.objects.count() + users_count == 0:
                raise CommandError("Posts and comments are requested, but there are no users")
            if comments_count and not posts_count and not Post.objects.filter(status=Post.Status.PUBLISHED).exists():
                raise CommandError("Comments are requested, but there are no published posts")


            users = self.__create_users(fake, users_count)
            # categories = self.__create_named(Category, CATEGORY_NAMES)
            # tags = self.__creat_named(TAG, TAG_NAMES)
            posts = self.__create_posts(fake, posts_count)
            comments = self.__create_comments(fake, comments_count)





    def __clear(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()


    def __create_users(self, fake: Faker, count: int) -> int:
        used_emails: set[str] = set(User.objects.values_list("email", flat=True))
        password_hash: str = make_password(SEED_PASSWORD)
        users: list = []

        for _ in range(count):
            first, last = fake.first_name(), fake.last_name()
            base = slugify(f'{first} {last}').replace('-', '.')
            email, n = f"{base}@{EMAIL_DOMAIN}", 1

            while email in used_emails:
                n+=1
                email =  f"{base}{n}@{EMAIL_DOMAIN}"
            used_emails.add(email)
            users.append(User(
                email=email, first_name=first, last_name=last, password=password_hash,
            ))

        User.objects.bulk_create(users, batch_size=1000)
        return len(users)


    def __create_posts(self, fake: Faker, count: int) -> int:
        if not count:
            return 0
        



    def __create_comments(self, fake: Faker, count: int) -> int:
        if not count:
            return 0