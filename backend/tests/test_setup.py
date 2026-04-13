def test_pytest_is_working():
    # Este test siempre pasa. Si sale en verde, tu entorno está bien.
    assert True

def test_python_version():
    import sys
    # Verificamos que estamos usando Python 3
    assert sys.version_info.major == 3