class ASCNotFoundError(Exception):
    """Exceção para quando um arquivo ASC não for encontrado no banco de dados."""
    def __init__(self, asc_id):
        self.message = f"Arquivo ASC com ID {asc_id} não encontrado."
        super().__init__(self.message)


class ASCAlreadyExistsError(Exception):
    """Exceção para quando um arquivo ASC já existir no banco de dados."""
    def __init__(self, filename):
        self.message = f"Já existe um arquivo ASC com o nome '{filename}'."
        super().__init__(self.message)


class ASCProcessingError(Exception):
    """Exceção para erros no processamento do arquivo ASC."""
    def __init__(self, detail="Erro ao processar o arquivo ASC."):
        self.message = detail
        super().__init__(self.message)
