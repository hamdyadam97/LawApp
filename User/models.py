import re
import uuid
from idlelib.pyparse import trans

from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import PermissionsMixin, UserManager as DjangoUserManager
from rest_framework_simplejwt.tokens import RefreshToken



def validate_username_user(username):
    pattern = re.compile("^(?=[a-zA-Z0-9._]{3,20}$)(?!.*[_.]{2})[^_.].*[^_.]$")
    if pattern.match(username):
        return username
    else:
        raise ValidationError("The username field should be between 3 and 20 characters in length and may contain "
                              "characters, numbers, or special characters (_.), but not at the beginning or end.")


class UserManager(DjangoUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{f'{self.model.USERNAME_FIELD}__iexact': username})


def upload_to_profile_pic(instance, filename):
    return f'uploads/profile/{uuid.uuid4()}/{filename}'


class User(AbstractBaseUser, PermissionsMixin):
    class UserGenderChoices(models.TextChoices):
        MALE = 'male', "Male"
        FEMALE = 'female', "Female"
        PREFERE_NOT_TO_ANSWER = 'prefer_not_to_answer', "Prefere not to answer"

    class UserTypeChoices(models.TextChoices):
        USER = 'user', "User"
        ADMIN = 'admin', "Admin"
        LAWYER = 'lawyer', "Lawyer"
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=50,
        unique=True,
        help_text=_('Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, validate_username_user],
        error_messages={
            'unique': _("This username already exists."),
        },
    )
    user_type = models.CharField(max_length=100,choices=UserTypeChoices.choices,)
    id_document = models.CharField(max_length=100,null=True,blank=True)
    photo = models.ImageField(upload_to='image',blank=True,null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=25, choices=UserGenderChoices.choices, blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    role = models.CharField(max_length=50,null=True,blank=True)
    is_deactivated = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    office = models.ForeignKey('Office.Office', on_delete=models.SET_NULL, null=True, related_name='user')
    is_set_password = models.BooleanField(default=True)
    lawfirm = models.CharField(max_length=100, blank=True, null=True)
    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @cached_property
    def token(self):
        return RefreshToken.for_user(self)

