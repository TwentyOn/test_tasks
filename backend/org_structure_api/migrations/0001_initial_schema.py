from django.db import migrations


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="CREATE SCHEMA IF NOT EXISTS hitalent_tusk;",
            reverse_sql="DROP SCHEMA IF EXISTS hitalent_tusk CASCADE;",
        ),
    ]
