from django.db import migrations


def create_categories(apps, schema_editor):
    Category = apps.get_model("core", "Category")
    categories = [
        ("Ceļi", "Bedres, ietves, ceļa zīmes un citas ceļu problēmas."),
        ("Apgaismojums", "Ielu lampas un citas publiskā apgaismojuma problēmas."),
        ("Tīrība", "Atkritumi, grafiti un citas tīrības problēmas."),
        ("Drošība", "Problēmas, kas var ietekmēt sabiedrības drošību."),
    ]
    for name, description in categories:
        Category.objects.get_or_create(name=name, defaults={"description": description})


def remove_categories(apps, schema_editor):
    Category = apps.get_model("core", "Category")
    Category.objects.filter(name__in=["Ceļi", "Apgaismojums", "Tīrība", "Drošība"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_categories, remove_categories),
    ]
