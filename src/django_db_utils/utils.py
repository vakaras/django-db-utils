
def join(query, field, separator=u'; '):
    """ Joins query objects fields ``field`` by ``separator``.
    """

    return separator.join([getattr(obj, field) for obj in query])
