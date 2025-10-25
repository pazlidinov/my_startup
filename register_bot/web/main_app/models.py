from django.db import models


# Create your models here.
class Gym(models.Model):
    name = models.CharField(max_length=150)
    loc_lat = models.FloatField()
    loc_long = models.FloatField()
    secret_code = models.CharField(unique=True, max_length=10)
    qr_code = models.ImageField(upload_to="gym_img")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    Role = (
        ("directro", "Direktor"),
        ("employee", "Hodim"),
        ("client", "Mijoz"),
    )
    user_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=66)
    last_name = models.CharField(max_length=66)
    telegram_id = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=25)
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
    balanse = models.PositiveSmallIntegerField(default=0)
    balanse = models.PositiveSmallIntegerField(blank=True, null=True)
    price = models.BigIntegerField(default=0)
    trainer = models.BooleanField(default=False)
    is_active = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.gym + "_" + self.client


class Registration(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="gym_registration")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="client_registration"
    )
    trainer = models.BooleanField(default=False)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="payment_registration"
    )

    def __str__(self):
        return self.gym + "_" + self.client
