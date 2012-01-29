""" Variuos utility functions.
"""


import collections

from django.db import models
from django.http import HttpResponse

from pysheets.sheet import Sheet
from pysheets.spreadsheet import SpreadSheet
from pysheets.writers import SheetWriter, SpreadSheetWriter


def join(query, field, separator=u'; '):
    """ Joins query objects fields ``field`` by ``separator``.
    """

    return separator.join([getattr(obj, field) for obj in query])


def collect_fields(obj, exclude=None):
    """ Collects all non ForeignKey fields.
    """

    if exclude is None:
        exclude = ()

    fields = []
    for field in obj._meta.fields:
        if field.name not in exclude:
            fields.append(field)
    return fields


def dump_query_to_sheet(
        queryset, sheet=None, fields=None, exclude=None,
        join_rules=None,
        merge_rules=None):
    """ Dumps query to sheet.

    If ``sheet`` is None, then creates one.

    :param fields: what fields from object to include, if None then all.
    :param exclude:
        what fields from object to exclude, if None then none.
    :param join_rules: what relationships to join_rules by field.
    :param merge_rules:
        what relationships to merge_rules into sheet. (``get`` method
        must return an item or raise DoesNotExist error).
    :returns: sheet object.

    """

    if sheet is None:
        sheet = Sheet()

    if len(queryset) < 1:
        return sheet
    obj = queryset[0]

    if fields is None:
        fields = collect_fields(obj, exclude)

    def modifier(sheet, row):
        """ Changes fields to Unicode strings.
        """
        new_row = collections.defaultdict(unicode)
        for field_name, (obj, field) in row.items():
            if obj is not None:
                display_attr = 'get_{0}_display'.format(field.name)
                if hasattr(obj, display_attr):
                    new_row[field_name] = getattr(obj, display_attr)()
                else:
                    value = getattr(obj, field.name)
                    if value is None:
                        new_row[field_name] = u''
                    else:
                        new_row[field_name] = value
            else:
                new_row[field_name] = field
        return new_row

    sheet.add_insert_validator(modifier)
    sheet.add_columns([field.verbose_name for field in fields])

    mergable = {}
    joinable = {}
    merge_rules = merge_rules or ()
    join_rules = join_rules or ()
    for related_obj in obj._meta.get_all_related_objects():
        if related_obj.name in merge_rules:
            model = related_obj.model
            merge_fields = collect_fields(model, ('id',))
            mergable[related_obj.name] = merge_fields, model
            sheet.add_columns([
                field.verbose_name
                for field in merge_fields
                ])
        for field_name, model_name, kwargs in join_rules:
            if model_name == related_obj.name:
                model = related_obj.model
                field = model._meta.get_field(field_name)
                joinable[related_obj.name.split(':')[1]] = field, kwargs
                print dir(field)
                sheet.add_column(field.verbose_name)
                break

    for obj in queryset:
        row = dict([(field.verbose_name, (obj, field)) for field in fields])
        for full_name, (merge_fields, model) in mergable.items():
            name = full_name.split(':')[1]
            try:
                related_obj = getattr(obj, name)
                for field in merge_fields:
                    row[field.verbose_name] = related_obj, field
            except model.DoesNotExist:
                pass
        for name, (field, (filter_kwargs, exclude_kwargs)) in (
                joinable.items()):
            query = getattr(obj, '{0}_set'.format(name)).all()
            print name, field, query
            row[field.verbose_name] = None, join(
                    query.filter(**filter_kwargs).exclude(**exclude_kwargs),
                    field.name)
        sheet.append_dict(row)

    return sheet


def download_query(queryset, writer_type, **kwargs):
    """ Generates sheet from queryset for downloading.

    :param writer_type: Sheet writer short name.
    """

    try:
        writer = SheetWriter.plugins[writer_type]
        data = dump_query_to_sheet(queryset, **kwargs)
    except KeyError:
        writer = SpreadSheetWriter.plugins[writer_type]
        data = SpreadSheet()
        sheet = data.create_sheet(u'Duomenys')
        dump_query_to_sheet(queryset, sheet, **kwargs)

    response = HttpResponse(mimetype=writer.mime_type)
    response['Content-Disposition'] = (
            'attachment; filename=duomenys.{0}'.format(
                writer.file_extensions[0]))
    data.write(response, writer=writer())
    return response
