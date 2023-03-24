# import views
from app.common.blueprint import EnhancedBlueprint
from .configuration import blp as config_blp
from .metadata import blp as metadata_blp

# v1 blueprint
blp = EnhancedBlueprint("v1", __name__)
# register config blueprint
blp.register_blueprint(config_blp)
# register metadata blueprint
blp.register_blueprint(metadata_blp)
