import unittest
import inspect

import tests.test_providers.sample_implemented as sample_implemented

# Keep the tests running in the order they were declared:
loader = unittest.TestLoader()
test_src = inspect.getsource(sample_implemented.SceneTest)
loader.sortTestMethodsUsing = lambda x, y: (
    test_src.index(f"def {x}") - test_src.index(f"def {y}")
)

try:
    unittest.main(
        argv=["-v", "sample_implemented.SceneTest"],
        exit=False,
        failfast=True,
        testLoader=loader,
    )
except Exception as e:
    print(e)
