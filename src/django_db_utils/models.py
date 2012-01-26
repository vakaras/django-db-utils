from uuid import uuid4 as uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

from db_utils.validators.name import (
        NamesValidator, SurnameValidator, ALPHABET_LT)
from db_utils.validators.phone_number import PhoneNumberValidator
from django_db_utils import forms


class FirstNameField(models.CharField):
    """ Model field for first name.
    """

    description = _("First name")
    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 45)
        kwargs['verbose_name'] = kwargs.get('verbose_name', _('First name'))
        models.CharField.__init__(self, **kwargs)
        self.validators.append(
                NamesValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),
                )

    def formfield(self, **kwargs):
        """ Creates form field for ModelForm.
        """
        defaults = {
                'form_class': forms.FirstNameField,
                }
        defaults.update(kwargs)
        return super(FirstNameField, self).formfield(**defaults)


class LastNameField(models.CharField):
    """ Model field for last name.
    """

    description = _("Last name")
    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 45)
        kwargs['verbose_name'] = kwargs.get('verbose_name', _('Last name'))
        models.CharField.__init__(self, **kwargs)
        self.validators.append(
                SurnameValidator(
                    ALPHABET_LT,
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),
                )

    def formfield(self, **kwargs):
        """ Creates form field for ModelForm.
        """
        defaults = {
                'form_class': forms.LastNameField,
                }
        defaults.update(kwargs)
        return super(LastNameField, self).formfield(**defaults)


class UUIDField(models.CharField):
    """ Unique identifier, which is automatically generated.
    """

    description = _("UUID")
    def __init__(self, **kwargs):
        kwargs['max_length'] = 36
        kwargs['unique'] = True
        kwargs['blank'] = True
        models.CharField.__init__(self, **kwargs)

    def pre_save(self, model_instance, add):
        """ If UUID is not already set, then sets one.
        """
        if not getattr(model_instance, self.attname):
            value = str(uuid())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UUIDField, self).pre_save(model_instance, add)


class PhoneNumberField(models.CharField):
    """ Model field for phone number.
    """

    description = _("Phone number")
    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 16)
        kwargs['verbose_name'] = kwargs.get(
                'verbose_name', _('Phone number'))
        models.CharField.__init__(self, **kwargs)
        self.validators.append(
                PhoneNumberValidator(
                    u'370',
                    validation_exception_type=ValidationError,
                    convert=False,
                    ),
                )

    def formfield(self, **kwargs):
        """ Creates form field for ModelForm.
        """

        defaults = {
                'form_class': forms.PhoneNumberField,
                }
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)
