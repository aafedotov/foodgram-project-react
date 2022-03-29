from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class CustomUser(AbstractUser):
    """Описываем кастомную модель пользователя."""
    email = models.EmailField(unique=True, max_length=254,
                              verbose_name='email')
    # username = models.CharField(unique=True,
    #                             validators=[validate_username],
    #                             max_length=150,
    #                             verbose_name='Имя пользователя')
    # date_joined = models.DateTimeField(verbose_name='дата создания',
    #                                    auto_now_add=True)
    # last_login = models.DateTimeField(verbose_name='последний вход в систему',
    #                                   auto_now=True)
    # is_admin = models.BooleanField(default=False,
    #                                verbose_name='Администратор')
    # is_active = models.BooleanField(default=True,
    #                                 verbose_name='активный')
    # is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False,
    #                                    verbose_name='Суперпользователь')
    # first_name = models.CharField(max_length=150, verbose_name='Имя')
    # last_name = models.CharField(max_length=150, verbose_name='Фамилия')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']


    # objects = CustomUserManager()

    @property
    def is_admin_or_superuser(self):
        """Описываем свойства для пермишенов."""
        return self.is_staff or self.is_superuser

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True


# class CustomUserManager(BaseUserManager):
#     """Описываем кастомную модель пользователя."""
#
#     def create_user(self, username, email, password, first_name, last_name):
#         if not email:
#             raise ValueError('e-mail обязателен для регистрации!')
#         if not username:
#             raise ValueError('username обязателен для регистрации!')
#         if not password:
#             raise ValueError('пароль обязателен для регистрации!')
#         if not first_name:
#             raise ValueError('имя обязательно для регистрации!')
#         if not last_name:
#             raise ValueError('фамилия обязательна для регистрации!')
#
#         user = self.model(
#             email=self.normalize_email(email),
#             username=username,
#             password=password,
#             first_name=first_name,
#             last_name=last_name,
#         )
#
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(
#             self, email, username, password, first_name, last_name
#     ):
#         user = self.create_user(
#             email=self.normalize_email(email),
#             password=password,
#             username=username,
#             first_name=first_name,
#             last_name=last_name,
#         )
#         user.is_admin = True
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user



