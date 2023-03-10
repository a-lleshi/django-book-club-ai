# Generated by Django 3.2.5 on 2022-04-04 16:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('bio', models.CharField(blank=True, max_length=520)),
                ('personal_statement', models.CharField(help_text='This statement is sent to any clubs you apply to. It can be changed at any time.', max_length=520)),
                ('location', models.CharField(max_length=30)),
                ('age', models.IntegerField(blank=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ISBN', models.CharField(max_length=13)),
                ('BookTitle', models.CharField(max_length=150)),
                ('BookAuthor', models.CharField(max_length=150)),
                ('YearOfPublication', models.CharField(max_length=4)),
                ('Publisher', models.CharField(max_length=150)),
                ('ImageURLS', models.CharField(max_length=300)),
                ('ImageURLM', models.CharField(max_length=300)),
                ('ImageURLL', models.CharField(max_length=300)),
            ],
            options={
                'ordering': ['ISBN'],
            },
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('location', models.CharField(blank=True, max_length=150)),
                ('description', models.CharField(blank=True, max_length=1000)),
                ('theme', models.CharField(blank=True, max_length=100)),
                ('choosing_book', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name', 'location', 'theme'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=520)),
                ('date', models.DateTimeField()),
                ('location', models.CharField(max_length=30)),
                ('clubs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_club.club')),
            ],
        ),
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userId', models.IntegerField()),
                ('ISBN', models.CharField(max_length=20)),
                ('bookRating', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=280)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='club_id', to='book_club.club')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EventComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=280)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_club.event')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=280)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_club.post')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ClubReadingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_club.book')),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_club.club')),
            ],
        ),
        migrations.CreateModel(
            name='ClubBookAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ISBN', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_club.book')),
                ('clubs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_club.club')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicationStatement', models.CharField(blank=True, max_length=1000)),
                ('level', models.CharField(choices=[('APP', 'Applicant'), ('MEM', 'Member'), ('OFF', 'Officer'), ('OWN', 'Owner')], default='APP', max_length=3)),
                ('club', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='book_club.club')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
                'unique_together': {('club', 'user')},
            },
        ),
        migrations.CreateModel(
            name='CurrentlyViewing',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='book_club.user')),
                ('club', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='book_club.club')),
            ],
        ),
        migrations.CreateModel(
            name='CurrentlyReading',
            fields=[
                ('book', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='book_club.book')),
                ('club', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='book_club.club')),
            ],
        ),
        migrations.AddConstraint(
            model_name='clubbookassignment',
            constraint=models.UniqueConstraint(fields=('clubs', 'ISBN'), name='unique_club_book_pair'),
        ),
    ]
