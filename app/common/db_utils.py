from sqlalchemy.exc import NoResultFound

from app import db


def _extract_model_params(defaults, **kwargs):
    defaults = defaults or {}
    ret = {}
    ret.update(kwargs)
    ret.update(defaults)
    return ret


def _create_object_from_params(session, model, params):
    obj = model(**params)
    session.add(obj)
    session.flush()
    return obj


def update_or_create(model, session=None, defaults=None, **kwargs):
    session = session if session is not None else db.session

    defaults = defaults or {}
    try:
        obj = session.query(model).filter_by(**kwargs).one()
    except NoResultFound:
        params = _extract_model_params(defaults, **kwargs)
        obj = _create_object_from_params(session, model, params)
        return obj, True
    for key, value in defaults.items():
        setattr(obj, key, value)
    session.add(obj)
    session.flush()
    return obj, False


def upsert_by_id(model, data: dict, session=None):
    """

    :param model: db model
    :param data: data of the model to be inserted/updated
    :param session: db session
    :return:returns the orm model object
    """
    _id = data.pop("id", None)
    session = session if session is not None else db.session
    instance, _ = update_or_create(model, session=session, defaults=data, id=_id)
    return instance


def get_or_create(model, session=None, defaults=None, **kwargs):
    session = session if session is not None else db.session
    try:
        return session.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        params = _extract_model_params(defaults, **kwargs)
        return _create_object_from_params(session, model, params), True
