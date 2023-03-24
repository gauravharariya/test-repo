from app.common.db_utils import (
    _create_object_from_params,
    _extract_model_params,
    get_or_create,
    update_or_create,
    upsert_by_id,
)
from app.models import Domain


def test_create_object_from_params(db_session):
    # When
    domain_params = {"name": "claims", "database": "RAW", "db_schema": "test"}

    domain = _create_object_from_params(db_session, Domain, domain_params)

    # Then
    assert domain.id is not None
    assert domain.name == domain_params["name"]
    assert domain.database == domain_params["database"]
    assert domain.db_schema == domain_params["db_schema"]

    # delete the domain
    db_session.delete(domain)
    db_session.commit()


def test_extract_model_params():
    # Given
    defaults = {"name": "Default Name", "email": "default@example.com"}

    # When
    params = {"name": "John", "age": 25}

    model_params = _extract_model_params(defaults, **params)

    # Then
    assert model_params["name"] == defaults["name"]
    assert model_params["age"] == params["age"]
    assert model_params["email"] == defaults["email"]


def test_get_or_create(db_session):
    # create a domain object
    domain = Domain(name="claims_101", database="RAW", db_schema="test")

    # add and commit the object to the database
    db_session.add(domain)
    db_session.commit()

    # check if the get_or_create function returns the object correctly
    obj, created = get_or_create(Domain, session=db_session, name="claims_101")
    assert obj.name == "claims_101"
    assert obj.db_schema == "test"
    assert not created

    # check if the function creates a new object if it doesn't exist in the database
    obj, created = get_or_create(
        Domain, session=db_session, name="claims_102", database="RAW", db_schema="test"
    )
    assert obj.name == "claims_102"
    assert created


def test_update_or_create(db_session):

    # Create a new object
    obj, created = update_or_create(
        Domain, db_session, name="claims_103", database="RAW", db_schema="test"
    )
    assert created
    assert obj.name == "claims_103"
    assert obj.db_schema == "test"

    # Update an existing object
    obj, created = update_or_create(
        Domain,
        db_session,
        name="claims_103",
        defaults=dict(database="CURATED", db_schema="new_db_schema"),
    )
    assert created is False
    assert obj.name == "claims_103"
    assert obj.database == "CURATED"
    assert obj.db_schema == "new_db_schema"


def test_upsert_by_id(db_session):
    # Create initial record
    domain = Domain(name="claims_104", database="RAW", db_schema="test")
    db_session.add(domain)
    db_session.commit()

    # Test updating an existing record
    data = {"id": domain.id, "database": "CURATED"}
    updated_domain = upsert_by_id(Domain, data, db_session)
    assert updated_domain.name == "claims_104"
    assert updated_domain.database == "CURATED"

    # Test creating a new record
    data = {"name": "claims_105", "database": "CURATED", "db_schema": "test"}
    new_domain = upsert_by_id(Domain, data, db_session)
    assert new_domain.id is not None
    assert new_domain.name == "claims_105"
    assert new_domain.database == "CURATED"
