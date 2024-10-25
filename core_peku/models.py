import datetime
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


class Category(models.Model):
    name  = models.CharField(max_length=255)
    icon  = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name


class Transaction(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.amount} on {self.date} - {self.category}'


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    def update_remaining(self):
        self.remaining_amount = self.allocated_amount - self.spent_amount
        self.save()

    def __str__(self):
        return f"{self.category}: {self.allocated_amount}"



class SavingGoal(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name       = models.CharField(max_length=100)
    target_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date     = models.DateTimeField()

    def __str__(self):
        return f"{self.goal_name}: {self.current_amount}/{self.target_amount}"

class Income(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    source      = models.CharField(max_length=100)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    date        = models.DateField(auto_now=False)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.source}: {self.amount}"
    
class Investment(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    investment_type = models.CharField(max_length=100)
    initial_amount  = models.DecimalField(max_digits=10, decimal_places=2)
    current_value   = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date   = models.DateTimeField()

    def __str__(self):
        return f"{self.investment_type}: {self.current_value}"