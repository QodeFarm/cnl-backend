import pytest

@pytest.mark.usefixtures("fixDemo1")
class testuser():
    def test_user(self):
        mass = "hi"
        assert mass == "hi", "Failed"

    def test_user2(self):
        mass = "hello"
        assert mass == "hi", "Failed"

    # @pytest.mark.xfail(reason="Feature not implemented yet")
    def test_user3(self):
        print("HIIIIIIIIIIIIIIIIii")
        mass = "hi"
        assert mass == "hi", "Failed"

    def test_user4(self, fixDemo1):
        a =9
        b = 10
        print(fixDemo1[0])
        assert a+10 == 19 , "Failed"


    def test_user5():
        print("Possible")
        name = "chetan"
        assert name == "chetan", "Not Matched"