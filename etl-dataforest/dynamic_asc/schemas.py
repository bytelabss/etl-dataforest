import uuid
from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length, Range


class AscFileSchema(Schema):
    """Schema para validar e serializar arquivos ASC."""

    id = fields.UUID(dump_only=True)
    user_id = fields.Str(required=True)
    filename = fields.Str(required=True)
    rows = fields.Int(required=True)
    cols = fields.Int(required=True)
    raster = fields.List(fields.List(fields.Float()), required=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates("filename")
    def validate_filename(self, value):
        """Garante que o nome do arquivo termine em .asc"""
        if not value.lower().endswith(".asc"):
            raise ValidationError("O nome do arquivo deve terminar com '.asc'.")


# Criando schemas para uso
asc_file_schema = AscFileSchema()
asc_files_schema = AscFileSchema(many=True)
