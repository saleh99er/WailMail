from emailParser import *

def condition_tests():
    condition_grades = Condition("(cms or gradescope) or piazza or cornell.edu")
    result = condition_grades.eval()
    assert(result == False)
    
    condition_grades.setTrue("fake")
    result = condition_grades.eval()
    assert(result == False)

    condition_grades.setTrue("gradescope")
    result = condition_grades.eval()
    assert(result == True)

    condition_grades.setTrue("cornell.edu")
    result = condition_grades.eval()
    assert(result == True)
    
    condition_workday = Condition("workday and not (timestamp and due)")
    result = condition_workday.eval()
    assert(result == False)

    condition_workday.setTrue("workday")
    result = condition_workday.eval()
    assert(result == True)

    condition_workday.setTrue("timestamp")
    result = condition_workday.eval()
    assert(result == True)

    condition_workday.setTrue("due")
    result = condition_workday.eval()
    assert(result == False)

    condition_campus = Condition("not north and not northcampus")
    result = condition_campus.eval()
    assert(result == True)

    condition_campus.setTrue("north")
    result = condition_campus.eval()
    assert(result == False)

    print("Condition class tests passed")

def rule_tests():

condition_tests()