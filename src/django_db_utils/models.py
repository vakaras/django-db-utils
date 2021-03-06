# -*- coding: utf-8 -*-

from uuid import uuid4 as uuid

from django.core.exceptions import ValidationError
from django.core import validators
from django.db import models
from django.utils.translation import ugettext as _

from django_db_utils.forms import (
        NamesValidator, SurnameValidator, EXTENDED_ALPHABET,
        PhoneNumberValidator, IdentityCodeValidator)
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
                    EXTENDED_ALPHABET,
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
                    EXTENDED_ALPHABET,
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


class IdentityCodeField(models.CharField):
    """ Model field for last name.
    """

    description = _("Identity code")
    def __init__(self, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 11)
        kwargs['verbose_name'] = kwargs.get(
                'verbose_name', _(u'Identity code'))
        kwargs['null'] = kwargs.get('null', True)
        models.CharField.__init__(self, **kwargs)
        self._identity_code_validator = IdentityCodeValidator(
                validation_exception_type=ValidationError,
                )
        self.validators.append(
                lambda text : unicode(self._identity_code_validator(text)))

    def formfield(self, **kwargs):
        """ Creates form field for ModelForm.
        """
        defaults = {
                'form_class': forms.IdentityCodeField,
                }
        defaults.update(kwargs)
        return super(IdentityCodeField, self).formfield(**defaults)


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


class PostalNumberField(models.CharField):
    """ Model field for postal number.
    """

    description = _("Postal number")
    def __init__(self, **kwargs):
        length = kwargs.get('length', 5)
        kwargs['max_length'] = kwargs.get('max_length', length)
        kwargs['verbose_name'] = kwargs.get(
                'verbose_name', _('Postal number'))
        models.CharField.__init__(self, **kwargs)
        self.validators.append(validators.MaxLengthValidator(length))
        self.validators.append(validators.MinLengthValidator(length))
        self.validators.append(validators.RegexValidator(r'^\d*$'))
