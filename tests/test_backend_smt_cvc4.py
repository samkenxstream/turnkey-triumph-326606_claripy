import unittest
from unittest import skipIf
import claripy
from claripy.backends.backend_smtlib_solvers.cvc4_popen import SolverBackendCVC4
import common_backend_smt_solver
from common_backend_smt_solver import if_installed


class SmtLibSolverTest_CVC4(common_backend_smt_solver.SmtLibSolverTestBase):
    @if_installed
    def get_solver(self):
        backend = SolverBackendCVC4(daggify=True)
        solver = claripy.SolverStrings(backend=backend, timeout=300000)
        return solver


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(SmtLibSolverTest_CVC4)
    unittest.TextTestRunner(verbosity=2).run(suite)
