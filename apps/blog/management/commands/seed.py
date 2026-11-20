from django.core.management import BaseCommand, CommandParser, CommandError
from typing import Any
from django.db import transaction
from faker import Faker
from apps.blog.models import Comment, Tag, Post, Category
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from random import random, choice, sample, randint


DEFAULT_USERS = 20
DEFAULT_POSTS = 100
DEFAULT_COMMENTS = 500
SEED_PASSWORD = "seedpass123"
EMAIL_DOMAIN = "example.com"
INACTIVE_RATIO = 0.1
STAFF_RATIO = 0.1
PUBLISHED_RATIO = 0.7
NO_CATEGORY_RATIO = 0.1
MIN_TAGS, MAX_TAGS = 0, 5
MIN_PARAGRAPHS, MAX_PARAGRAPHS = 3, 6
MIN_SENTENCES, MAX_SENTENCES = 1, 3

CATEGORY_NAMES = ["Python", "Django", "DevOps", "Databases", "Testing", "Security", "Frontend", "Career"]
TAG_NAMES = ["orm", "migrations", "docker", "git", "postgresql", "sqlite", "api", "admin", "unfold",
             "faker", "pytest", "linux", "ci-cd", "performance", "caching", "typing", "async",
             "deployment", "tips", "tutorial"]

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

        fake = Faker()


        with transaction.atomic():
            if options["clear"]:
                self.__clear()
            if (posts_count or comments_count) and User.objects.count() + users_count == 0:
                raise CommandError("Posts and comments are requested, but there are no users")
            if comments_count and not posts_count and not Post.objects.filter(status=Post.Status.PUBLISHED).exists():
                raise CommandError("Comments are requested, but there are no published posts")


            users = self.__create_users(fake, users_count)
            categories = self.__create_named(Category, CATEGORY_NAMES)
            tags = self.__create_named(Tag, TAG_NAMES)
            posts = self.__create_posts(fake, posts_count)
            comments = self.__create_comments(fake, comments_count)

        self.stdout.write(self.style.SUCCESS(
            f"Users:      {users:>4} created\n"
            f"Categories: {categories:>4} created\n"
            f"Tags:       {tags:>4} created\n"
            f"Posts:      {posts:>4} created\n"
            f"Comments:   {comments:>4} created\n"
            # f"Done in {time.perf_counter() - start:.2f} seconds"
        ))




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
    
    def __create_named(self, model: type, names: list[str]) -> int:
        existing: set[str] = set(model.objects.values_list('name', flat=True))

        new = [
            model(name=n, slug = slugify(n))
            for n in names
            if n not in existing
        ]

        model.objects.bulk_create(new)
        return len(new)
    
    
    @staticmethod
    def __unique_slug(title: str, used: set[str]) -> str:
        base = slugify(title)[: 50] or "post"   # SlugField default max is 50
        slug, n = base, 1
        while slug in used:
            n += 1
            suffix = f"-{n}"
            slug = base[: 50 - len(suffix)] + suffix
        used.add(slug)
        return slug



    def __create_posts(self, fake: Faker, count: int) -> int:
        if not count:
            return 0

        author_ids = list(User.objects.values_list('pk', flat=True))
        category_ids = list(Category.objects.values_list('pk', flat=True))
        tag_ids = list(Tag.objects.values_list('pk', flat=True))
        used_slugs: set[str] = set(Post.objects.values_list('slug', flat=True))

        posts: list[Post] = []

        for _ in range(count):
            title= fake.sentence(nb_words=4).rstrip('.')
            posts.append(Post(
                author_id = choice(author_ids),
                title=title,
                slug=self.__unique_slug(title, used_slugs),
                body="\n\n".join(fake.paragraphs(nb=randint(MIN_PARAGRAPHS, MAX_PARAGRAPHS))),
                category_id=None if random() < NO_CATEGORY_RATIO or not category_ids
                            else choice(category_ids),
                status=Post.Status.PUBLISHED if random() < PUBLISHED_RATIO else Post.Status.DRAFT,
            ))
        Post.objects.bulk_create(posts, batch_size=1000)



        for post in posts:
            k = randint(MIN_TAGS, min(MAX_TAGS, len(tag_ids)))
            if k:
                post.tags.set(sample(tag_ids, k))
        return len(posts)



    def __create_comments(self, fake: Faker, count: int) -> int:
        if not count:
            return 0

        published_ids = list(Post.objects.filter(status=Post.Status.PUBLISHED).values_list('pk', flat=True))


        if not published_ids:
            raise CommandError("comments are requested but there are not any published posts")

        author_ids=list(User.objects.values_list('pk', flat=True))

        comments = [
            Comment(
                post_id=choice(published_ids),
                author_id = choice(author_ids),
                body=" ".join(fake.sentences(nb=randint(MIN_SENTENCES, MAX_SENTENCES))),
            )
            for _ in range(count)
        ]

        Comment.objects.bulk_create(comments, batch_size=1000)
        return len(comments)