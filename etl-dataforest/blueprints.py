from .dynamic_asc.blueprints import bp as dynamic_asc_bp
from .dynamic_shp.blueprints import bp as dynamic_shp_bp


def init_blueprints(app):
    app.register_blueprint(dynamic_asc_bp)
    app.register_blueprint(dynamic_shp_bp)

