from .dynamic_asc.blueprints import bp as dynamic_asc_bp


def init_blueprints(app):
    app.register_blueprint(dynamic_asc_bp)

