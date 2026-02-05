from marshmallow_sqlalchemy import ModelConversionError, ModelSchema
from marshmallow import fields
from sqlalchemy.sql.schema import ForeignKeyConstraint
from sqlalchemy.orm import mapper, configure_mappers
from sqlalchemy import event


def get_two_way_relationship_cols(main_class, related_class):
    two_way_relationship_cols = []
    for relationship in related_class.__mapper__.relationships.items():
        if relationship[1].mapper.class_ == main_class:
            two_way_relationship_cols.append(relationship[0])
    return two_way_relationship_cols


def get_relationships_dict(class_):
    relationships_dict = {}
    for relationship in class_.__mapper__.relationships.items():
        relationship_schema_class_name = "%sSchema" % relationship[1].mapper.class_.__name__
        relationships_dict[relationship[0]] = \
            fields.Nested(relationship_schema_class_name, many=relationship[1].uselist,
                          exclude=get_two_way_relationship_cols(class_, relationship[1].mapper.class_))
    return relationships_dict


def get_fks_dict(class_):
    fks_dict = {}
    for constraint in class_.__table__.constraints:
        if isinstance(constraint, ForeignKeyConstraint):
            base_columns = constraint.columns[constraint.column_keys[0]].base_columns
            nullable = False if not base_columns else base_columns.pop().nullable
            fks_dict[constraint._col_description] = fields.Integer(allow_none=nullable)
    return fks_dict


def setup_schema(Base, session):
    # Create a function which incorporates the Base and session information
    def setup_schema_fn():
        for class_ in Base._decl_class_registry.values():
            if hasattr(class_, "__tablename__") and not hasattr(class_, "Schema"):
                if class_.__name__.endswith("Schema"):
                    raise ModelConversionError(
                        "For safety, setup_schema can not be used when a"
                        "Model class ends with 'Schema'"
                    )
                schema_class_name = "%sSchema" % class_.__name__

                class Meta(object):
                    model = class_
                    sqla_session = session
                schema_dict = {"Meta": Meta}
                schema_dict.update(get_relationships_dict(class_))
                schema_dict.update(get_fks_dict(class_))

                schema_class = type(schema_class_name, (ModelSchema,), schema_dict)

                setattr(class_, "Schema", schema_class)

    return setup_schema_fn


def init_db_schema(db):
    event.listen(mapper, "after_configured", setup_schema(db.Base, db.session), once=True)
    # Use configure_mappers so that "after_configured" event will occur.
    configure_mappers()
