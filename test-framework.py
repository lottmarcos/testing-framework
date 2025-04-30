class TestCase:
    """
    Classe base para casos de teste.
    Todas as classes de teste devem herdar desta classe.
    """

    def __init__(self, test_method_name):
        """
        Inicializa um caso de teste com o nome do método de teste.

        Args:
            test_method_name: Nome do método a ser executado como teste
        """
        self.test_method_name = test_method_name

    def run(self, result):
        """
        Executa o teste seguindo o padrão template method e registra os resultados.

        Args:
            result: Objeto TestResult para armazenar os resultados da execução
        """
        result.test_started()
        self.set_up()
        try:
            test_method = getattr(self, self.test_method_name)
            test_method()
        except AssertionError as e:
            result.add_failure(self.test_method_name)
        except Exception as e:
            result.add_error(self.test_method_name)
        self.tear_down()

    def set_up(self):
        """
        Método executado antes de cada teste.
        Pode ser sobrescrito nas subclasses para inicializar recursos.
        """
        pass

    def tear_down(self):
        """
        Método executado após cada teste.
        Pode ser sobrescrito nas subclasses para liberar recursos.
        """
        pass


class TestResult:
    """
    Classe responsável por coletar e sumarizar os resultados da execução dos testes.
    """
    RUN_MSG = 'run'
    FAILURE_MSG = 'failed'
    ERROR_MSG = 'error'

    def __init__(self, suite_name=None):
        self.run_count = 0
        self.failures = []
        self.errors = []

    def test_started(self):
        """
        Incrementa o contador de testes executados.
        """
        self.run_count += 1

    def add_failure(self, test):
        """
        Adiciona um teste à lista de falhas.

        Args:
            test: Nome do método de teste que falhou (AssertionError)
        """
        self.failures.append(test)

    def add_error(self, test):
        """
        Adiciona um teste à lista de erros.

        Args:
            test: Nome do método de teste que gerou erro (Exception)
        """
        self.errors.append(test)

    def summary(self):
        """
        Retorna um resumo dos resultados dos testes.

        Returns:
            String com formato "X run, Y failed, Z error"
        """
        return f'{self.run_count} {self.RUN_MSG}, ' \
               f'{str(len(self.failures))} {self.FAILURE_MSG}, ' \
               f'{str(len(self.errors))} {self.ERROR_MSG}'