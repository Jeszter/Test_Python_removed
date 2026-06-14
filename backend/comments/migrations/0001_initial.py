import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CaptchaChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64, unique=True, verbose_name='Key')),
                ('answer', models.CharField(max_length=10, verbose_name='Answer')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used', models.BooleanField(default=False, verbose_name='Used')),
            ],
            options={
                'verbose_name': 'CAPTCHA',
                'verbose_name_plural': 'CAPTCHAs',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100, verbose_name='User name')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('homepage', models.URLField(blank=True, null=True, verbose_name='Home page')),
                ('text', models.TextField(verbose_name='Comment text')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/%Y/%m/%d/', verbose_name='Image')),
                ('attachment', models.FileField(blank=True, null=True, upload_to='files/%Y/%m/%d/', verbose_name='File')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP address')),
                ('user_agent', models.TextField(blank=True, verbose_name='Browser User-Agent')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='comments.comment', verbose_name='Parent comment')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['-created_at'], name='comments_co_created_77d8cb_idx'),
                    models.Index(fields=['username'], name='comments_co_usernam_67764f_idx'),
                    models.Index(fields=['email'], name='comments_co_email_2d2846_idx'),
                    models.Index(fields=['parent'], name='comments_co_parent__0f7f1c_idx'),
                ],
            },
        ),
    ]
