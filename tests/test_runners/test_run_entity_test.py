import unittest
import inspect

import tests.test_providers.sample_implemented as sample_implemented

# Keep the tests running in the order they were declared:
loader = unittest.TestLoader()
test_src = inspect.getsource(sample_implemented.EntityTest)
loader.sortTestMethodsUsing = lambda x, y: (
    test_src.index(f"def {x}") - test_src.index(f"def {y}")
)

try:
    unittest.main(
        argv=["-v", "sample_implemented.EntityTest"],
        exit=False,
        failfast=True,
        testLoader=loader,
    )
except Exception as e:
    print(e)
