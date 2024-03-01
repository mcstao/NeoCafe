from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from branches.models import Branch


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, first_name=None, last_name=None, **extra_fields):
        if not email:
            raise ValueError("Пользователи должны иметь электронную почту")

        user = self.model(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            first_name="Super",
            last_name="User",
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class EmployeeSchedule(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    monday = models.BooleanField(default=False)
    monday_start_time = models.TimeField(null=True, blank=True)
    monday_end_time = models.TimeField(null=True, blank=True)

    tuesday = models.BooleanField(default=False)
    tuesday_start_time = models.TimeField(null=True, blank=True)
    tuesday_end_time = models.TimeField(null=True, blank=True)

    wednesday = models.BooleanField(default=False)
    wednesday_start_time = models.TimeField(null=True, blank=True)
    wednesday_end_time = models.TimeField(null=True, blank=True)

    thursday = models.BooleanField(default=False)
    thursday_start_time = models.TimeField(null=True, blank=True)
    thursday_end_time = models.TimeField(null=True, blank=True)

    friday = models.BooleanField(default=False)
    friday_start_time = models.TimeField(null=True, blank=True)
    friday_end_time = models.TimeField(null=True, blank=True)

    saturday = models.BooleanField(default=False)
    saturday_start_time = models.TimeField(null=True, blank=True)
    saturday_end_time = models.TimeField(null=True, blank=True)

    sunday = models.BooleanField(default=False)
    sunday_start_time = models.TimeField(null=True, blank=True)
    sunday_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class CustomUser(AbstractBaseUser, PermissionsMixin):
    POSITIONS = (("barista", "Barista"), ("waiter", "Waiter"), ("client", "Client"), ("admin", "Admin"),)

    first_name = models.CharField(max_length=255, blank=True, null=True)
    schedule = models.ForeignKey(
        EmployeeSchedule,
        on_delete=models.CASCADE,
        related_name="employees",
        null=True,
        blank=True,
    )
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    birth_date = models.DateField(blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    otp = models.CharField(max_length=4, blank=True, null=True)
    branch = models.ForeignKey(
        to=Branch, on_delete=models.CASCADE, null=True, blank=True
    )
    bonus = models.IntegerField(default=0)
    position = models.CharField(max_length=255, choices=POSITIONS, default="client")
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("Группы"),
        blank=True,
        help_text=_(
            "Группы, к которым принадлежит пользователь. Пользователь получит все разрешения, предоставленные каждой из его групп."
        ),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("Права пользователя"),
        blank=True,
        help_text=_("Конкретные права для этого пользователя."),
        related_name="customuser_permissions",
        related_query_name="customuser",
    )

    def __str__(self):
        return f"Пользователь: {self.first_name} - {self.email}"
