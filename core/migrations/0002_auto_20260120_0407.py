from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(unique=True, max_length=150)),
                ('full_name', models.CharField(max_length=200, blank=True, help_text='Full name of the admin')),  # <-- added
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_staff', models.BooleanField(default=True, help_text='Can access Django admin')),  # default True like your model
                ('is_active', models.BooleanField(default=True, help_text='Can this user login?')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(
                    to='auth.Group',
                    verbose_name='groups',
                    blank=True,
                    related_name='admin_users',
                    related_query_name='admin_user',
                )),
                ('user_permissions', models.ManyToManyField(
                    to='auth.Permission',
                    verbose_name='user permissions',
                    blank=True,
                    related_name='admin_users',
                    related_query_name='admin_user',
                )),
            ],
            options={
                'verbose_name': 'Admin User',
                'verbose_name_plural': 'Admin Users',
                'ordering': ['-date_joined'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
