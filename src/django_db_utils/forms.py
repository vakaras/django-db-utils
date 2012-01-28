# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import ugettext as _

from pysheets.spreadsheet import SpreadSheet
from pysheets.readers import SheetReader, SpreadSheetReader

from db_utils.validators.name import (
        NamesValidator, SurnameValidator, ALPHABET_LT)
from db_utils.validators.phone_number import PhoneNumberValidator
from db_utils.validators.identity_code import IdentityCodeValidator


EXTENDED_ALPHABET = ALPHABET_LT + (u'x', u'w', u'q', u'ä', u'ü', u'ö', u'ß')


class FirstNameField(forms.CharField):
    """ Form field for first name.
    """

    def __init__(self, *args, **kwargs):
        super(FirstNameField, self).__init__(*args, **kwargs)
        self._validator = NamesValidator(
                EXTENDED_ALPHABET,
                validation_exception_type=ValidationError,
                )

    def clean(self, value):
        """ Cleans value, to contain Unicode string or None.
        """

        value = super(FirstNameField, self).clean(value)
        if not value and not self.required:
            return value
        else:
            return self._validator(value)


class LastNameField(forms.CharField):
    """ Form field for last name.
    """

    def __init__(self, *args, **kwargs):
        super(LastNameField, self).__init__(*args, **kwargs)
        self._validator = SurnameValidator(
                EXTENDED_ALPHABET,
                validation_exception_type=ValidationError,
                )

    def clean(self, value):
        """ Cleans value, to contain Unicode string or None.
        """

        value = super(LastNameField, self).clean(value)
        if not value and not self.required:
            return value
        else:
            return self._validator(value)


class IdentityCodeField(forms.CharField):
    """ Form field for last name.
    """

    def __init__(self, *args, **kwargs):
        super(IdentityCodeField, self).__init__(*args, **kwargs)
        self._validator = IdentityCodeValidator(
                validation_exception_type=ValidationError,
                )

    def clean(self, value):
        """ Cleans value, to contain Unicode string or None.
        """

        value = super(IdentityCodeField, self).clean(value)
        if not value and not self.required:
            return value
        else:
            return unicode(self._validator(value))


class PhoneNumberField(forms.CharField):
    """ Form field for phone number.
    """

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = kwargs.get('initial', u'+370')
        super(PhoneNumberField, self).__init__(*args, **kwargs)
        self._validator = PhoneNumberValidator(
                u'370',
                validation_exception_type=ValidationError,
                )

    def clean(self, value):
        """ Cleans value, to contain Unicode string with phone number
        or None.
        """

        if value == u'+370':
            value = u''

        value = super(PhoneNumberField, self).clean(value)
        if not value and not self.required:
            return value
        else:
            return self._validator(value)


class SheetField(forms.FileField):
    """ Form field for spreadsheet.
    """

    def __init__(
            self, sheet_name_column=_(u'Sheet'),
            sheet_constructor_args=None,
            spreadsheet_constructor_args=None,
            *args, **kwargs):
        super(SheetField, self).__init__(*args, **kwargs)
        self.sheet_name_column = sheet_name_column
        self.sheet_constructor_args = sheet_constructor_args or {}
        self.spreadsheet_constructor_args = (
                spreadsheet_constructor_args or {})

    def clean(self, value, initial):
        """ Cleans value to contain Sheet.
        """

        value = super(SheetField, self).clean(value, initial)
        try:
            reader = SpreadSheetReader.plugins.get_by_file(value.name)
        except KeyError:
            try:
                reader = SheetReader.plugins.get_by_file(value.name)
            except KeyError:
                raise forms.ValidationError(
                        _(u'Failed to recognize file type.'))
            else:
                pass
                # TODO
        else:
            spreadsheet = SpreadSheet(
                    value, reader=reader(),
                    **self.spreadsheet_constructor_args)
            return spreadsheet.join(self.sheet_name_column)
