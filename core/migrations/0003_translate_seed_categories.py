from django.db import migrations


def translate_categories(apps, schema_editor):
    Category = apps.get_model("core", "Category")
    translations = {
        "Roads": ("Ceļi", "Bedres, ietves, ceļa zīmes un citas ceļu problēmas."),
        "Lighting": ("Apgaismojums", "Ielu lampas un citas publiskā apgaismojuma problēmas."),
        "Cleanliness": ("Tīrība", "Atkritumi, grafiti un citas tīrības problēmas."),
        "Safety": ("Drošība", "Problēmas, kas var ietekmēt sabiedrības drošību."),
    }
    for old_name, (new_name, description) in translations.items():
        Category.objects.filter(name=old_name).update(name=new_name, description=description)


def restore_categories(apps, schema_editor):
    Category = apps.get_model("core", "Category")
    translations = {
        "Ceļi": ("Roads", "Potholes, sidewalks, traffic signs and other road issues."),
        "Apgaismojums": ("Lighting", "Street lights and other public lighting problems."),
        "Tīrība": ("Cleanliness", "Trash, graffiti and other cleanliness issues."),
        "Drošība": ("Safety", "Issues that can affect public safety."),
    }
    for old_name, (new_name, description) in translations.items():
        Category.objects.filter(name=old_name).update(name=new_name, description=description)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_seed_categories"),
    ]

    operations = [
        migrations.RunPython(translate_categories, restore_categories),
    ]
