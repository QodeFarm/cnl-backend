import pytest


def test_user():
    mass = "hi"
    assert mass == "hi", "Failed"

def test_user2():
    mass = "hello"
    assert mass == "hi", "Failed"

@pytest.mark.xfail(reason="Feature not implemented yet")
def test_user3():
    print("HIIIIIIIIIIIIIIIIii")
    mass = "hi"
    assert mass == "hi", "Failed"

def test_user4():
    a =9
    b = 10
    assert a+10 == 19 , "Failed"