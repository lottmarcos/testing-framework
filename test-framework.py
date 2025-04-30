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

    # Comandos Assert personalizados
    def assert_equal(self, first, second):
        """
        Verifica se dois objetos são iguais.

        Args:
            first: Primeiro objeto a ser comparado
            second: Segundo objeto a ser comparado

        Raises:
            AssertionError: Se os objetos não forem iguais
        """
        if first != second:
            msg = f'{first} != {second}'
            raise AssertionError(msg)

    def assert_true(self, expr):
        """
        Verifica se uma expressão é verdadeira.

        Args:
            expr: Expressão a ser verificada

        Raises:
            AssertionError: Se a expressão for falsa
        """
        if not expr:
            msg = f'{expr} is not true'
            raise AssertionError(msg)

    def assert_false(self, expr):
        """
        Verifica se uma expressão é falsa.

        Args:
            expr: Expressão a ser verificada

        Raises:
            AssertionError: Se a expressão for verdadeira
        """
        if expr:
            msg = f'{expr} is not false'
            raise AssertionError(msg)

    def assert_in(self, member, container):
        """
        Verifica se um elemento está contido em um container.

        Args:
            member: Elemento a ser verificado
            container: Container a ser verificado

        Raises:
            AssertionError: Se o elemento não estiver no container
        """
        if member not in container:
            msg = f'{member} not found in {container}'
            raise AssertionError(msg)


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
        self.assert_equal(self.result.summary(), '1 run, 0 failed, 0 error')

    def test_result_failure_run(self):
        stub = TestStub('test_failure')
        stub.run(self.result)
        self.assert_equal(self.result.summary(), '1 run, 1 failed, 0 error')

    def test_result_error_run(self):
        stub = TestStub('test_error')
        stub.run(self.result)
        self.assert_equal(self.result.summary(), '1 run, 0 failed, 1 error')

    def test_result_multiple_run(self):
        stub = TestStub('test_success')
        stub.run(self.result)
        stub = TestStub('test_failure')
        stub.run(self.result)
        stub = TestStub('test_error')
        stub.run(self.result)
        self.assert_equal(self.result.summary(), '3 run, 1 failed, 1 error')

    def test_was_set_up(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        self.assert_true(spy.was_set_up)

    def test_was_run(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        self.assert_true(spy.was_run)

    def test_was_tear_down(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        self.assert_true(spy.was_tear_down)

    def test_template_method(self):
        spy = TestSpy('test_method')
        spy.run(self.result)
        self.assert_equal(spy.log, "set_up test_method tear_down")

    # Testes para os métodos de asserção
    def test_assert_true(self):
        self.assert_true(True)

    def test_assert_false(self):
        self.assert_false(False)

    def test_assert_equal(self):
        self.assert_equal("", "")
        self.assert_equal("foo", "foo")
        self.assert_equal([], [])
        self.assert_equal(['foo'], ['foo'])
        self.assert_equal((), ())
        self.assert_equal(('foo',), ('foo',))
        self.assert_equal({}, {})
        self.assert_equal({'foo'}, {'foo'})

    def test_assert_in(self):
        animals = {'monkey': 'banana', 'cow': 'grass', 'seal': 'fish'}
        self.assert_in('a', 'abc')
        self.assert_in('foo', ['foo'])
        self.assert_in(1, [1, 2, 3])
        self.assert_in('monkey', animals)

# Classe para testar TestSuite
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

        self.assert_equal(len(suite.tests), 3)

    def test_suite_success_run(self):
        result = TestResult()
        suite = TestSuite()
        suite.add_test(TestStub('test_success'))

        suite.run(result)

        self.assert_equal(result.summary(), '1 run, 0 failed, 0 error')

    def test_suite_multiple_run(self):
        result = TestResult()
        suite = TestSuite()
        suite.add_test(TestStub('test_success'))
        suite.add_test(TestStub('test_failure'))
        suite.add_test(TestStub('test_error'))

        suite.run(result)

        self.assert_equal(result.summary(), '3 run, 1 failed, 1 error')


# Classe para testar TestLoader
class TestLoaderTest(TestCase):
    """
    Classe que testa o comportamento da classe TestLoader.
    """
    def test_create_suite(self):
        loader = TestLoader()
        suite = loader.make_suite(TestStub)
        self.assert_equal(len(suite.tests), 3)

    def test_create_suite_of_suites(self):
        loader = TestLoader()
        stub_suite = loader.make_suite(TestStub)
        spy_suite = loader.make_suite(TestSpy)

        suite = TestSuite()
        suite.add_test(stub_suite)
        suite.add_test(spy_suite)

        self.assert_equal(len(suite.tests), 2)

    def test_get_multiple_test_case_names(self):
        loader = TestLoader()
        names = loader.get_test_case_names(TestStub)
        self.assert_equal(names, ['test_error', 'test_failure', 'test_success'])

    def test_get_no_test_case_names(self):
        class Test(TestCase):
            def foobar(self):
                pass

        loader = TestLoader()
        names = loader.get_test_case_names(Test)
        self.assert_equal(names, [])


# Exemplo de uso dos métodos de asserção personalizados
class AssertExampleTest(TestCase):
    """
    Exemplo de uso dos métodos de asserção personalizados.
    """
    def test_assert_basic_examples(self):
        # Verificações básicas
        self.assert_true(1 < 2)
        self.assert_false(1 > 2)
        self.assert_equal(1 + 1, 2)
        self.assert_in(3, [1, 2, 3, 4])

    def test_assert_with_different_types(self):
        # Demonstração com diversos tipos de dados
        self.assert_equal("hello", "hello")
        self.assert_true(bool([1, 2]))  # Lista não vazia é avaliada como True
        self.assert_false(bool([]))     # Lista vazia é avaliada como False
        self.assert_in("key", {"key": "value"})


def run_all_tests():
    """
    Executa todos os testes do framework e exibe um relatório consolidado.
    Agora inclui os testes para os comandos assert.
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
    assert_example_suite = loader.make_suite(AssertExampleTest)

    # Imprime informações sobre os testes encontrados
    print(f"Testes de TestCase: {len(test_case_suite.tests)} testes")
    print(f"Testes de TestSuite: {len(test_suite_suite.tests)} testes")
    print(f"Testes de TestLoader: {len(test_loader_suite.tests)} testes")
    print(f"Testes de AssertExample: {len(assert_example_suite.tests)} testes")
    print("-"*50)

    # Cria uma suíte principal para agregar todas as outras
    main_suite = TestSuite()
    main_suite.add_test(test_case_suite)
    main_suite.add_test(test_suite_suite)
    main_suite.add_test(test_loader_suite)
    main_suite.add_test(assert_example_suite)

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
    print("Framework de teste com comandos assert")
    print("Escolha uma opção:")
    print("1 - Executar um teste específico")
    print("2 - Executar todos os testes de uma classe")
    print("3 - Executar todos os testes do framework")
    print("4 - Executar exemplos de uso dos comandos assert")

    option = input("Opção: ")

    if option == "1":
        # Exemplo de execução de um teste específico
        print("\nExecutando um teste específico (TestCaseTest.test_assert_equal)")
        result = TestResult()
        test = TestCaseTest('test_assert_equal')
        test.run(result)
        print(result.summary())

    elif option == "2":
        # Exemplo de execução de todos os testes de uma classe
        print("\nExecutando todos os testes da classe AssertExampleTest")
        loader = TestLoader()
        suite = loader.make_suite(AssertExampleTest)
        runner = TestRunner()
        runner.run(suite)

    elif option == "3":
        # Executa todos os testes do framework
        run_all_tests()

    elif option == "4":
        # Exemplos simples de uso dos comandos assert
        print("\nExemplos de uso dos comandos assert:")

        try:
            # Exemplo que deve passar
            print("Verificando assert_equal (deve passar):")
            example = AssertExampleTest('test_assert_basic_examples')
            result = TestResult()
            example.run(result)
            print("OK!")

            # Exemplo que deve falhar
            print("\nVerificando assert_equal (deve falhar):")
            class FailingTest(TestCase):
                def test_failing(self):
                    self.assert_equal(1, 2)  # Falha intencional

            failing = FailingTest('test_failing')
            result = TestResult()
            failing.run(result)
            print(f"Falha registrada: {result.failures}")

        except Exception as e:
            print(f"Erro: {e}")

    else:
        print("Opção inválida!")