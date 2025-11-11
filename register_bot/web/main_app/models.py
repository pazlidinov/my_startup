from django.db import models


# Create your models here.
class Gym(models.Model):
    name = models.CharField(max_length=150)
    loc_lat = models.FloatField()
    loc_long = models.FloatField()
    secret_code = models.CharField(unique=True, max_length=10)
    qr_code = models.ImageField(upload_to="gym_img")
    lump_sum = models.PositiveIntegerField(default=0)
    lump_trainer_sum = models.PositiveIntegerField(default=0, blank=True, null=True)
    balance = models.PositiveSmallIntegerField
    date_and = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    Role = (
        ("directro", "Direktor"),
        ("employee", "Hodim"),
        ("client", "Mijoz"),
    )
    Languages = (
        ("lotin", "Lotincha"),
        ("kiril", "Кирилча"),
        ("rus", " Русский язык"),
    )
    user_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=66)
    last_name = models.CharField(max_length=66)
    telegram_id = models.CharField(unique=True, max_length=20)
    phone_number = models.CharField(max_length=25)
    language = models.CharField(choices=Languages, max_length=25)
    secret_code = models.CharField(unique=True, max_length=10)
    qr_code = models.ImageField(upload_to="client_img")
    role = models.CharField(choices=Role, max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_name


class Payment(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="gym_payment")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_payment"
    )
    count = models.PositiveSmallIntegerField(default=0)
    balanse = models.PositiveSmallIntegerField(blank=True, null=True)
    price = models.BigIntegerField(default=0)
    date_start = models.DateField(auto_now_add=True)
    date_end = models.DateField(blank=True, null=True)
    is_trainer = models.BooleanField(default=False)
    is_active = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.gym + "_" + self.client


class Registration(models.Model):
    gym = models.ForeignKey(
        Gym, on_delete=models.CASCADE, related_name="gym_registration"
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_registration"
    )
    is_trainer = models.BooleanField(default=False)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="payment_registration"
    )

    def __str__(self):
        return self.gym + "_" + self.client


class Admin(models.Model):
    user_name = models.CharField(max_length=100)
    telegram_id = models.CharField(unique=True, max_length=20)

    def __str__(self):
        return self.user_name
