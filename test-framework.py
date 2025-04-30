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


class TestLoader:
    """
    Responsável por descobrir e carregar testes automaticamente.
    """
    TEST_METHOD_PREFIX = 'test'

    def get_test_case_names(self, test_case_class):
        """
        Encontra todos os métodos da classe que começam com o prefixo de teste.

        Args:
            test_case_class: Classe de teste da qual extrair os métodos

        Returns:
            Lista ordenada com os nomes dos métodos de teste
        """
        methods = dir(test_case_class)
        test_method_names = list(filter(lambda method:
            method.startswith(self.TEST_METHOD_PREFIX), methods))
        return sorted(test_method_names)

    def make_suite(self, test_case_class):
        """
        Cria uma suíte de teste contendo todos os métodos de teste da classe.

        Args:
            test_case_class: Classe de teste para criar a suíte

        Returns:
            TestSuite contendo todos os testes da classe
        """
        suite = TestSuite()
        for test_method_name in self.get_test_case_names(test_case_class):
            test_method = test_case_class(test_method_name)
            suite.add_test(test_method)
        return suite


class TestRunner:
    """
    Orquestra a execução dos testes e fornece relatórios.
    """
    def __init__(self):
        """
        Inicializa o runner de teste com um novo objeto TestResult.
        """
        self.result = TestResult()

    def run(self, test):
        """
        Executa o teste ou suíte de testes e gera o relatório.

        Args:
            test: Um objeto TestCase ou TestSuite a ser executado

        Returns:
            O objeto TestResult com os resultados da execução
        """
        test.run(self.result)
        print(self.result.summary())
        return self.result


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


# Classe para testar TestLoader
class TestLoaderTest(TestCase):
    """
    Classe que testa o comportamento da classe TestLoader.
    """
    def test_create_suite(self):
        loader = TestLoader()
        suite = loader.make_suite(TestStub)
        assert len(suite.tests) == 3

    def test_create_suite_of_suites(self):
        loader = TestLoader()
        stub_suite = loader.make_suite(TestStub)
        spy_suite = loader.make_suite(TestSpy)

        suite = TestSuite()
        suite.add_test(stub_suite)
        suite.add_test(spy_suite)

        assert len(suite.tests) == 2

    def test_get_multiple_test_case_names(self):
        loader = TestLoader()
        names = loader.get_test_case_names(TestStub)
        assert names == ['test_error', 'test_failure', 'test_success']

    def test_get_no_test_case_names(self):
        class Test(TestCase):
            def foobar(self):
                pass

        loader = TestLoader()
        names = loader.get_test_case_names(Test)
        assert names == []


def run_all_tests():
    """
    Executa todos os testes do framework e exibe um relatório consolidado.

    Esta função usa TestLoader para descobrir automaticamente todos os
    testes nas classes de teste, agrupa-os em uma TestSuite principal e
    executa-os usando um TestRunner.
    """
    print("="*50)
    print("Executando todos os testes do framework")
    print("="*50)

    # Cria um loader para descobrir os testes automaticamente
    loader = TestLoader()

    # Cria suítes individuais para cada classe de teste
    test_case_suite = loader.make_suite(TestCaseTest)
    test_suite_suite = loader.make_suite(TestSuiteTest)
    test_loader_suite = loader.make_suite(TestLoaderTest)

    # Imprime informações sobre os testes encontrados
    print(f"Testes de TestCase: {len(test_case_suite.tests)} testes")
    print(f"Testes de TestSuite: {len(test_suite_suite.tests)} testes")
    print(f"Testes de TestLoader: {len(test_loader_suite.tests)} testes")
    print("-"*50)

    # Cria uma suíte principal para agregar todas as outras
    main_suite = TestSuite()
    main_suite.add_test(test_case_suite)
    main_suite.add_test(test_suite_suite)
    main_suite.add_test(test_loader_suite)

    # Executa todos os testes usando um TestRunner
    runner = TestRunner()
    result = runner.run(main_suite)

    # Fornece informações adicionais sobre a execução
    print("-"*50)
    print(f"Total de testes executados: {result.run_count}")
    if len(result.failures) > 0:
        print(f"Falhas: {result.failures}")
    if len(result.errors) > 0:
        print(f"Erros: {result.errors}")
    print("="*50)

    return result


# Demonstração do uso do framework
if __name__ == "__main__":
    print("Escolha uma opção:")
    print("1 - Executar um teste específico")
    print("2 - Executar todos os testes de uma classe")
    print("3 - Executar todos os testes do framework")

    option = input("Opção: ")

    if option == "1":
        # Exemplo de execução de um teste específico
        print("\nExecutando um teste específico (TestLoaderTest.test_create_suite)")
        result = TestResult()
        test = TestLoaderTest('test_create_suite')
        test.run(result)
        print(result.summary())

    elif option == "2":
        # Exemplo de execução de todos os testes de uma classe
        print("\nExecutando todos os testes da classe TestLoaderTest")
        loader = TestLoader()
        suite = loader.make_suite(TestLoaderTest)
        runner = TestRunner()
        runner.run(suite)

    elif option == "3":
        # Executa todos os testes do framework
        run_all_tests()

    else:
        print("Opção inválida!")