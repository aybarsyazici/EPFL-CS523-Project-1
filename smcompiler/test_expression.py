"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret, Scalar, Expression

tests = {
    repr(Secret(1) + Secret(2)): "Secret(1) + Secret(2)",
    repr(Secret(2) * Secret(1)): "Secret(2) * Secret(1)",
    repr(Secret() + Secret() + Secret() + Scalar(5)): "Secret() + Secret() + Secret() + Scalar(5)",
    #repr((Secret() + Secret()) + (Secret() + Scalar(5))): "(Secret() + Secret()) + (Secret() + Scalar(5))",
    repr(Secret(1) * Secret(2) * Secret(3)): "Secret(1) * Secret(2) * Secret(3)",
    repr(Secret(1) * (Secret(2) + Secret(3) * Scalar(4))): "Secret(1) * (Secret(2) + Secret(3) * Scalar(4))",
    repr((Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3)): "(Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3)",
    repr(Secret(1) + Secret(2) * Secret(3) * Scalar(4) + Scalar(3)): "Secret(1) + Secret(2) * Secret(3) * Scalar(4) + Scalar(3)",
}

tree_tests: list[Expression] = [
    (Secret(1) + Secret(2)),
    (Secret(1) * Secret(2) + Secret(3)),
    (Secret(1) * (Secret(2) + Secret(3) * Scalar(4))),
    ((Secret(5) - Secret(2)) * (Secret(8) + Secret(14))),
    (Secret(1) + Secret(2) * (Scalar(15) + Scalar(15) * Scalar(3))),
    ((Secret(1) * Secret(2)) + (Secret(3) * Secret(4))) + (Secret(5) * Secret(6)),
]

# Example test, you can adapt it to your needs.
def test_expr_construction():
    for expr, expected in tests.items():
        print(f"Testing {expr} == {expected}")
        assert expr == expected
        print("Passed!")

def test_tree():
    for test in tree_tests:
        test.print_tree()
        print()
        print("==================================")
        print()


def test_unix_tree():
    for test in tree_tests:
        test.print_tree_unix()
        print("_________________")

if __name__ == "__main__":
    #test_expr_construction()
    #test_unix_tree()
    test_tree()