# Generated by Django 4.2.1 on 2023-06-01 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forumApp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="video",
            field=models.FileField(blank=True, null=True, upload_to="video/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc1",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc2",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc3",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc4",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc5",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc6",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc7",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc8",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="post",
            name="picSrc9",
            field=models.ImageField(blank=True, null=True, upload_to="posts/"),
        ),
        migrations.AlterField(
            model_name="user",
            name="imageSrc",
            field=models.ImageField(default="avatar.jpg", upload_to="photos/"),
        ),
    ]
