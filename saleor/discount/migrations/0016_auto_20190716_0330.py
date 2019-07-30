# Generated by Django 2.2.3 on 2019-07-16 08:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("discount", "0015_voucher_min_quantity_of_products")]

    operations = [
        migrations.AddField(
            model_name="voucher",
            name="apply_once_per_customer",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="VoucherCustomer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("customer_email", models.EmailField(max_length=254)),
                (
                    "voucher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customers",
                        to="discount.Voucher",
                    ),
                ),
            ],
            options={"unique_together": {("voucher", "customer_email")}},
        ),
    ]