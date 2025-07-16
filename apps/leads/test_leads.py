import pytest


@pytest.mark.usefixtures()
class testLeads():
    def test_leads1():
        mass = "hi"
        assert mass == "hi", "Failed"

    def test_leads3():
        mass = "hi"
        assert mass == "hi", "Failed"

    def test_leads():
        mass = "hi"
        assert mass == "hi", "Failed"

    def test_leads2(fixDemo1):
        mass = "hi"
        print(fixDemo1[1])
        assert mass == "hi", "Failed"