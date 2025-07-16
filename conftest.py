import pytest

@pytest.fixture()
def fixDemo1():
    print("Before Executing")
    yield
    print("AFTER Executing")
    return ['chetan', 'akshay', 'pk']