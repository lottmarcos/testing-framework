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


class TestSuite:
    """
    Representa uma coleção de casos de teste.
    Implementa o padrão Composite para permitir que uma suíte seja
    tratada da mesma forma que um caso de teste individual.
    """
    def __init__(self):
        self.tests = []

    def add_test(self, test):
        """
        Adiciona um teste à suíte.
        O teste pode ser um TestCase ou outro TestSuite.

        Args:
            test: TestCase ou TestSuite a ser adicionado
        """
        self.tests.append(test)

    def run(self, result):
        """
        Executa todos os testes na suíte, coletando os resultados.

        Args:
            result: Objeto TestResult para armazenar os resultados da execução
        """
        for test in self.tests:
            test.run(result)


# Classe auxiliar que simula uma classe de teste com diferentes tipos de resultados
class TestStub(TestCase):
    """
    Classe stub usada para testar o framework de teste.
    Contém métodos de teste que simulam diferentes resultados (sucesso, falha e erro).
    """
    def test_success(self):
        assert True

    def test_failure(self):
        assert False

    def test_error(self):
        raise Exception


# Classe spy para verificar o comportamento do template method
class TestSpy(TestCase):
    """
    Classe que espiona a execução do template method.
    Registra quando e em que ordem os métodos são executados.
    """
    def __init__(self, name):
        TestCase.__init__(self, name)
        self.was_run = False
        self.was_set_up = False
        self.was_tear_down = False
        self.log = ""

    def set_up(self):
        self.was_set_up = True
        self.log += "set_up "

    def test_method(self):
        self.was_run = True
        self.log += "test_method "

    def tear_down(self):
        self.was_tear_down = True
        self.log += "tear_down"


# Classe para testar TestCase
class TestCaseTest(TestCase):
    """
    Classe que testa o comportamento da classe TestCase.
    """
    def set_up(self):
        self.result = TestResult()

    def test_result_success_run(self):
        stub = TestStub('test_success')
        stub.run(self.result)
        assert self.result.summary() == '1 run, 0 failed, 0 error'

    def test_result_failure_run(self):
        stub = TestStub('test_failure')
        stub.run(self.result)
        assert self.result.summary() == '1 run, 1 failed, 0 error'

    def test_result_error_run(self):
        stub = TestStub('test_error')
        stub.run(self.result)
        assert self.result.summary() == '1 run, 0 failed, 1 error'

    def test_result_multiple_run(self):
        stub = TestStub('test_success')
        stub.run(self.result)
        stub = TestStub('test_failure')
        stub.run(self.result)
        stub = TestStub('test_error')
        stub.run(self.result)
        assert self.result.summary() == '3 run, 1 failed, 1 error'

    def test_was_set_up(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.was_set_up

    def test_was_run(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.was_run

    def test_was_tear_down(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.was_tear_down

    def test_template_method(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        assert spy.log == "set_up test_method tear_down"


# Classe para testar TestSuite
class TestSuiteTest(TestCase):
    """
    Classe que testa o comportamento da classe TestSuite.
    """
    def test_suite_size(self):
        suite = TestSuite()

        suite.add_test(TestStub('test_success'))
        suite.add_test(TestStub('test_failure'))
        suite.add_test(TestStub('test_error'))

        assert len(suite.tests) == 3

    def test_suite_success_run(self):
        result = TestResult()
        suite = TestSuite()
        suite.add_test(TestStub('test_success'))

        suite.run(result)

        assert result.summary() == '1 run, 0 failed, 0 error'

    def test_suite_multiple_run(self):
        result = TestResult()
        suite = TestSuite()
        suite.add_test(TestStub('test_success'))
        suite.add_test(TestStub('test_failure'))
        suite.add_test(TestStub('test_error'))

        suite.run(result)

        assert result.summary() == '3 run, 1 failed, 1 error'


# Código para executar os testes
if __name__ == "__main__":
    # Executando os testes individuais para TestCase
    print("Executando testes para TestCase...")
    result = TestResult()

    test = TestCaseTest('test_result_success_run')
    test.run(result)
    test = TestCaseTest('test_result_failure_run')
    test.run(result)
    test = TestCaseTest('test_result_error_run')
    test.run(result)
    test = TestCaseTest('test_result_multiple_run')
    test.run(result)
    test = TestCaseTest('test_was_set_up')
    test.run(result)
    test = TestCaseTest('test_was_run')
    test.run(result)
    test = TestCaseTest('test_was_tear_down')
    test.run(result)
    test = TestCaseTest('test_template_method')
    test.run(result)

    print(result.summary())

    # Executando os testes para TestSuite
    print("\nExecutando testes para TestSuite...")
    result = TestResult()

    test = TestSuiteTest('test_suite_size')
    test.run(result)
    test = TestSuiteTest('test_suite_success_run')
    test.run(result)
    test = TestSuiteTest('test_suite_multiple_run')
    test.run(result)

    print(result.summary())

    # Executando todos os testes usando uma TestSuite
    print("\nExecutando todos os testes usando TestSuite...")
    result = TestResult()
    suite = TestSuite()

    # Adicionando todos os testes de TestCaseTest
    suite.add_test(TestCaseTest('test_result_success_run'))
    suite.add_test(TestCaseTest('test_result_failure_run'))
    suite.add_test(TestCaseTest('test_result_error_run'))
    suite.add_test(TestCaseTest('test_result_multiple_run'))
    suite.add_test(TestCaseTest('test_was_set_up'))
    suite.add_test(TestCaseTest('test_was_run'))
    suite.add_test(TestCaseTest('test_was_tear_down'))
    suite.add_test(TestCaseTest('test_template_method'))

    # Adicionando todos os testes de TestSuiteTest
    suite.add_test(TestSuiteTest('test_suite_size'))
    suite.add_test(TestSuiteTest('test_suite_success_run'))
    suite.add_test(TestSuiteTest('test_suite_multiple_run'))

    suite.run(result)
    print(result.summary())  # Deve mostrar "11 run, 0 failed, 0 error"