"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret, Scalar

tests = {
    repr(Secret(1) + Secret(2)): "Secret(1) + Secret(2)",
    repr(Secret(2) * Secret(1)): "Secret(2) * Secret(1)",
    repr(Secret(1) * Secret(2) * Secret(3)): "Secret(1) * Secret(2) * Secret(3)",
    repr(Secret(1) * (Secret(2) + Secret(3) * Scalar(4))): "Secret(1) * (Secret(2) + Secret(3) * Scalar(4))",
    repr((Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3)): "(Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3)",
}

# Example test, you can adapt it to your needs.
def test_expr_construction():
    for expr, expected in tests.items():
        print(f"Testing {expr} == {expected}")
        assert expr == expected
        print("Passed!")

if __name__ == "__main__":
    test_expr_construction()