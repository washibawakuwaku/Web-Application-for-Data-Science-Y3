from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PredictionLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("input_data", models.JSONField()),
                ("prediction", models.CharField(max_length=100)),
                ("probabilities", models.JSONField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
