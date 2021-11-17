import claripy
import unittest


class TestExpression(unittest.TestCase):
    def test_smudging(self):
        x = claripy.BVS('x', 32)
        y = x+1
        assert isinstance(y.args[1], claripy.ast.BV)
        assert y.args[1].args[0] == 1
        assert y.args[1].args[1] == 32

        x = claripy.BVS('x', 32)
        y = x*1
        z = y+1
        assert isinstance(y.args[1], claripy.ast.BV)
        assert y.args[1].args[0] == 1
        assert y.args[1].args[1] == 32

        assert isinstance(z.args[1], claripy.ast.BV)
        assert z.args[1].args[0] == 1
        assert z.args[1].args[1] == 32

        ccc = claripy.If(x > 10, x*3+2, x*4+2)
        assert isinstance(ccc.args[1].args[1], claripy.ast.BV)
        assert ccc.args[1].args[1].args[0] == 2
        assert ccc.args[1].args[1].args[1] == 32

        x = claripy.BVS('x', 32)
        y = x + "AAAA"
        assert isinstance(y.args[1], claripy.ast.BV)
        assert y.args[1].args[0] == 0x41414141
        assert y.args[1].args[1] == 32

    def test_expression(self):
        bc = claripy.backends.concrete

        e = claripy.BVV(0x01020304, 32)
        assert len(e) == 32
        r = e.reversed
        assert bc.convert(r) == 0x04030201
        assert len(r) == 32

        assert [ bc.convert(i) for i in r.chop(8) ] == [ 4, 3, 2, 1 ]

        e1 = r[31:24]
        assert bc.convert(e1) == 0x04
        assert len(e1) == 8
        assert bc.convert(e1[2]) == 1
        assert bc.convert(e1[1]) == 0

        ee1 = e1.zero_extend(8)
        assert bc.convert(ee1) == 0x0004
        assert len(ee1) == 16

        ee1 = claripy.BVV(0xfe, 8).sign_extend(8)
        assert bc.convert(ee1) == 0xfffe
        assert len(ee1) == 16

        xe1 = [ bc.convert(i) for i in e1.chop(1) ]
        assert xe1 == [ 0, 0, 0, 0, 0, 1, 0, 0 ]

        a = claripy.BVV(1, 1)
        assert bc.convert(a+a) == 2

        x = claripy.BVV(1, 32)
        assert x.length == 32
        y = claripy.LShR(x, 10)
        assert y.length == 32

        r = claripy.BVV(0x01020304, 32)
        rr = r.reversed
        rrr = rr.reversed
        #assert bc.convert(r) is bc.convert(rrr)
        #assert type(bc.convert(rr)) is claripy.A
        assert bc.convert(rr) == 0x04030201
        assert r.concat(rr) is claripy.Concat(r, rr)

        rsum = r+rr
        assert bc.convert(rsum) == 0x05050505

        r = claripy.BVS('x', 32)
        rr = r.reversed
        rrr = rr.reversed
        assert r is rrr

        # test identity
        assert r is rrr
        assert r is not rr
        ii = claripy.BVS('ii', 32)
        ij = claripy.BVS('ij', 32)
        assert ii is ii
        assert ii is not ij

        si = claripy.SI(bits=32, stride=2, lower_bound=20, upper_bound=100)
        sj = claripy.SI(bits=32, stride=2, lower_bound=10, upper_bound=10)
        sk = claripy.SI(bits=32, stride=2, lower_bound=20, upper_bound=100)
        assert claripy.backends.vsa.identical(si, si)
        assert not claripy.backends.vsa.identical(si, sj)
        assert claripy.backends.vsa.identical(si, sk)
        assert si is not sj
        assert sj is not sk
        assert sk is not si

        # test hash cache
        assert a+a is a+a

        # test replacement
        old = claripy.BVS('old', 32, explicit_name=True)
        new = claripy.BVS('new', 32, explicit_name=True)
        ooo = claripy.BVV(0, 32)

        old_formula = claripy.If((old + 1)%256 == 0, old+10, old+20)
        print(old_formula.dbg_repr())
        new_formula = old_formula.replace(old, new)
        print(new_formula.dbg_repr())
        ooo_formula = new_formula.replace(new, ooo)

        print(ooo_formula.dbg_repr())

        assert hash(old_formula) != hash(new_formula)
        assert hash(old_formula) != hash(ooo_formula)
        assert hash(new_formula) != hash(ooo_formula)

        assert old_formula.variables == { 'old' }
        assert new_formula.variables == { 'new' }
        assert ooo_formula.variables == ooo.variables

        assert old_formula.symbolic
        assert new_formula.symbolic
        assert new_formula.symbolic

        assert str(old_formula).replace('old', 'new') == str(new_formula)
        assert bc.convert(ooo_formula) == 20

        # test dict replacement
        old = claripy.BVS('old', 32, explicit_name=True)
        new = claripy.BVS('new', 32, explicit_name=True)
        c = (old + 10) - (old + 20)
        d = (old + 1) - (old + 2)
        cr = c.replace_dict({(old+10).cache_key: (old+1), (old+20).cache_key: (old+2)})
        assert cr is d

        # test AST collapse
        s = claripy.SI(bits=32, stride=0, lower_bound=10, upper_bound=10)
        b = claripy.BVV(20, 32)

        sb = s+b
        assert isinstance(sb.args[0], claripy.ast.Base)

        bb = b+b
        # this was broken previously -- it was checking if type(bb.args[0]) == A,
        # and it wasn't, but was instead a subclass. leaving this out for now
        # nose.tools.assert_not_is_instance(bb.args[0], claripy.ast.Base)

        # ss = s+s
        # (see above)
        # nose.tools.assert_not_is_instance(ss.args[0], claripy.ast.Base)

        sob = s|b
        # for now, this is collapsed. Presumably, Fish will make it not collapse at some point
        assert isinstance(sob.args[0], claripy.ast.Base)

        # make sure the AST collapses for delayed ops like reversing
        rb = b.reversed
        #assert isinstance(rb.args[0], claripy.ast.Base)
        # TODO: Properly delay reversing: should not be eager

        assert rb is not bb
        assert rb is rb

        # test some alternate bvv creation methods
        assert claripy.BVV('AAAA') is claripy.BVV(0x41414141, 32)
        assert claripy.BVV('AAAA', 32) is claripy.BVV(0x41414141, 32)
        assert claripy.BVV('AB') is claripy.BVV(0x4142, 16)
        assert claripy.BVV('AB', 16) is claripy.BVV(0x4142, 16)
        self.assertRaises(claripy.errors.ClaripyValueError, claripy.BVV, 'AB', 8)

    def test_cardinality(self):
        x = claripy.BVS('x', 32)
        y = claripy.BVS('y', 32, min=100, max=120)
        n = claripy.BVV(10, 32)
        m = claripy.BVV(20, 32)

        assert y.cardinality == 21
        assert x.cardinality == 2**32
        assert n.cardinality == 1
        assert m.cardinality == 1
        assert n.union(m).cardinality == 2
        assert n.union(y).cardinality == 111
        assert y.intersection(x).cardinality == 21
        assert n.intersection(m).cardinality == 0
        assert y.intersection(m).cardinality == 0

        assert n.singlevalued
        assert not n.multivalued

        assert y.multivalued
        assert not y.singlevalued

        assert not x.singlevalued
        assert x.multivalued

        assert not y.union(m).singlevalued
        assert y.union(m).multivalued

        assert not y.intersection(m).singlevalued
        assert not y.intersection(m).multivalued

    def test_if_stuff(self):
        x = claripy.BVS('x', 32)
        #y = claripy.BVS('y', 32)

        c = claripy.If(x > 10, (claripy.If(x > 10, x*3, x*2)), x*4) + 2
        cc = claripy.If(x > 10, x*3, x*4) + 2
        ccc = claripy.If(x > 10, x*3+2, x*4+2)
        cccc = x*claripy.If(x > 10, claripy.BVV(3, 32), claripy.BVV(4, 32)) + 2

        assert c is cc
        assert c.ite_excavated is ccc
        assert ccc.ite_burrowed is cccc

        i = c + c
        ii = claripy.If(x > 10, (x*3+2)+(x*3+2), (x*4+2)+(x*4+2))
        assert i.ite_excavated is ii

        cn = claripy.If(x <= 10, claripy.BVV(0x10, 32), 0x20)
        iii = c + cn
        iiii = claripy.If(x > 10, (x*3+2)+0x20, (x*4+2)+0x10)
        assert iii.ite_excavated is iiii

    def test_ite(self):
        yield raw_ite, claripy.Solver
        yield raw_ite, claripy.SolverHybrid
        yield raw_ite, claripy.SolverComposite

    def raw_ite(solver_type):
        s = solver_type()
        x = claripy.BVS("x", 32)
        y = claripy.BVS("y", 32)
        z = claripy.BVS("z", 32)

        ite = claripy.ite_dict(x, {1:11, 2:22, 3:33, 4:44, 5:55, 6:66, 7:77, 8:88, 9:99}, claripy.BVV(0, 32))
        assert sorted(s.eval(ite, 100)) == [ 0, 11, 22, 33, 44, 55, 66, 77, 88, 99 ]

        ss = s.branch()
        ss.add(ite == 88)
        assert sorted(ss.eval(ite, 100)) == [ 88 ]
        assert sorted(ss.eval(x, 100)) == [ 8 ]

        ity = claripy.ite_dict(x, {1:11, 2:22, 3:y, 4:44, 5:55, 6:66, 7:77, 8:88, 9:99}, claripy.BVV(0, 32))
        ss = s.branch()
        ss.add(ity != 11)
        ss.add(ity != 22)
        ss.add(ity != 33)
        ss.add(ity != 44)
        ss.add(ity != 55)
        ss.add(ity != 66)
        ss.add(ity != 77)
        ss.add(ity != 88)
        ss.add(ity != 0)
        ss.add(y == 123)
        assert sorted(ss.eval(ity, 100)) == [ 99, 123 ]
        assert sorted(ss.eval(x, 100)) == [ 3, 9 ]
        assert sorted(ss.eval(y, 100)) == [ 123 ]

        itz = claripy.ite_cases([ (claripy.And(x == 10, y == 20), 33), (claripy.And(x==1, y==2), 3), (claripy.And(x==100, y==200), 333) ], claripy.BVV(0, 32))
        ss = s.branch()
        ss.add(z == itz)
        ss.add(itz != 0)
        assert ss.eval(y/x, 100) == ( 2, )
        assert sorted(ss.eval(x, 100)) == [ 1, 10, 100 ]
        assert sorted(ss.eval(y, 100)) == [ 2, 20, 200 ]

    def test_ite_reverse(self):
        a = claripy.BVS('a', 32)
        cases = [(a == i, claripy.BVV(i, 32)) for i in range(30)]
        ast = claripy.ite_cases(cases, -1)
        ext_cases = list(claripy.reverse_ite_cases(ast))

        assert sum(1 if case.op == 'And' else 0 for case, _ in ext_cases)
        for case, val in ext_cases:
            if case.op == 'And':
                assert claripy.is_true(val == -1)
            else:
                assert any(case is orig_case and val is orig_val for orig_case, orig_val in cases)

    def test_bool(self):
        bc = claripy.backends.concrete

        a = claripy.And(*[False, False, True])
        assert bc.convert(a) == False
        a = claripy.And(*[True, True, True])
        assert bc.convert(a) == True

        o = claripy.Or(*[False, False, True])
        assert bc.convert(o) == True
        o = claripy.Or(*[False, False, False])
        assert bc.convert(o) == False

    def test_extract(self):
        a = claripy.BVS("a", 32)
        assert a[7:] is a[7:0]
        assert a[31:] is a
        assert a[:] is a
        assert a[:0] is a
        assert a[:-8] is a[31:24]
        assert a[-1:] is a[31:0]
        assert a[-1:-8] is a[31:24]

    def test_get_byte(self):
        a = claripy.BVV("ABCD")
        assert a.get_byte(1) is claripy.BVV("B")

    def test_extract_concat_simplify(self):
        a = claripy.BVS("a", 32)
        assert a[31:0] is a
        assert a[31:8].concat(a[7:0]) is a  # pylint:disable=no-member
        assert a[31:16].concat(a[15:8], a[7:0]) is a  # pylint:disable=no-member
        assert a[31:24].concat(a[23:16], a[15:8], a[7:0]) is a  # pylint:disable=no-member

        a = claripy.BVS("a", 32)
        b = a + 100
        b_concat = b[31:8].concat(b[7:0])
        a100 = a + 100
        assert claripy.is_false(b_concat == a100) is False
        assert list(claripy.Solver().eval(b_concat == a100, 2)) == [ True ]
        assert b_concat is a100
        assert claripy.is_true(b_concat == a100)

    def test_true_false_cache(self):
        claripy.backends._quick_backends.append(claripy.backends.z3)

        a = claripy.BVS("a_WILL_BE_VIOLATED", 32)
        c = a == a+1
        assert claripy.is_false(c)
        c.args[1].args = (a, claripy.BVV(0, 32))
        assert claripy.is_false(c)
        assert not claripy.is_true(c)
        assert not claripy.is_false(a == a)

        claripy.backends._quick_backends[-1:] = [ ]

    def test_depth_repr(self):
        x = claripy.BVS("x", 32)
        y = claripy.LShR(x, 10)
        y = claripy.LShR(y, 10)
        y = claripy.LShR(y, 10)
        y = claripy.LShR(y, 10)
        y = claripy.LShR(y, 10)
        y = claripy.LShR(y, 10)
        y = claripy.LShR(y, 10)
        print(y.shallow_repr(max_depth=5))
        assert y.shallow_repr(max_depth=5) == "<BV32 LShR(LShR(LShR(LShR(LShR(<...>, <...>), 0xa), 0xa), 0xa), 0xa)>"

    def test_rename(self):
        x1 = claripy.BVS('x', 32)
        x2 = x1._rename('y')
        print(x2.variables)
        assert x2.variables == frozenset(('y',))

    def test_canonical(self):
        x1 = claripy.BVS('x', 32)
        b1 = claripy.BoolS('b')
        c1 = claripy.BoolS('c')
        x2 = claripy.BVS('x', 32)
        b2 = claripy.BoolS('b')
        c2 = claripy.BoolS('c')

        assert x1.canonicalize()[-1] is x2.canonicalize()[-1]

        y1 = claripy.If(claripy.And(b1, c1), x1, ((x1+x1)*x1)+1)
        y2 = claripy.If(claripy.And(b2, c2), x2, ((x2+x2)*x2)+1)

        one_names = frozenset.union(x1.variables, b1.variables, c1.variables)
        two_names = frozenset.union(x2.variables, b2.variables, c2.variables)

        assert frozenset.union(*[a.variables for a in y1.recursive_leaf_asts]) == one_names
        assert frozenset.union(*[a.variables for a in y2.recursive_leaf_asts]) == two_names
        assert y1.canonicalize()[-1] is y2.canonicalize()[-1]

    def test_depth(self):
        x1 = claripy.BVS('x', 32)
        assert x1.depth == 1
        x2 = x1 + 1
        assert x2.depth == 2

    def test_multiarg(self):
        x = claripy.BVS('x', 32)
        o = claripy.BVV(2, 32)

        x_add = x+x+x+x
        x_mul = x*x*x*x
        x_sub = x-(x+1)-(x+2)-(x+3)
        x_or = x|(x+1)|(x+2)|(x+3)
        x_xor = x^(x+1)^(x+2)^(x+3)
        x_and = x&(x+1)&(x+2)&(x+3)

        assert x_add.variables == x.variables
        assert x_mul.variables == x.variables
        assert x_sub.variables == x.variables
        assert x_or.variables == x.variables
        assert x_xor.variables == x.variables
        assert x_and.variables == x.variables
        assert (claripy.BVV(1, 32)+(x+x)).variables == x.variables

        assert len(x_add.args) == 4
        assert len(x_mul.args) == 4
        #assert len(x_sub.args) == 4 # needs more work
        assert len(x_or.args) == 4
        assert len(x_xor.args) == 4
        assert len(x_and.args) == 4

        assert (x_add).replace(x, o).args[0] == 8
        assert (x_mul).replace(x, o).args[0] == 16
        assert (x_or).replace(x, o).args[0] == 7
        assert (x_xor).replace(x, o).args[0] == 0
        assert (x_and).replace(x, o).args[0] == 0
        assert (100 + (x_sub).replace(x, o)).args[0] == 90

        # make sure that all backends handle this properly
        for b in claripy.backends._all_backends:
            try:
                b.convert(x+x+x+x)
            except claripy.BackendError:
                pass
        print('ok')

    def test_signed_concrete(self):
        bc = claripy.backends.concrete
        a = claripy.BVV(5, 32)
        b = claripy.BVV(-5, 32)
        c = claripy.BVV(3, 32)
        d = claripy.BVV(-3, 32)

        # test unsigned
        assert bc.convert(a / c) == 1
        assert bc.convert(a / d) == 0
        assert bc.convert(b / c) == 0x55555553
        assert bc.convert(b / d) == 0
        assert bc.convert(a % c) == 2
        assert bc.convert(a % d) == 5
        assert bc.convert(b % c) == 2
        assert bc.convert(b % d) == -5

        # test unsigned
        assert bc.convert(a.SDiv(c)) == 1
        assert bc.convert(a.SDiv(d)) == -1
        assert bc.convert(b.SDiv(c)) == -1
        assert bc.convert(b.SDiv(d)) == 1
        assert bc.convert(a.SMod(c)) == 2
        assert bc.convert(a.SMod(d)) == 2
        assert bc.convert(b.SMod(c)) == -2
        assert bc.convert(b.SMod(d)) == -2

    def test_signed_symbolic(self):
        solver = claripy.Solver()
        a = claripy.BVS("a", 32)
        b = claripy.BVS("b", 32)
        c = claripy.BVS("c", 32)
        d = claripy.BVS("d", 32)
        solver.add(a == 5)
        solver.add(b == -5)
        solver.add(c == 3)
        solver.add(d == -3)

        # test unsigned
        assert list(solver.eval(a / c, 2)) == [1]
        assert list(solver.eval(a / d, 2)) == [0]
        assert list(solver.eval(b / c, 2)) == [0x55555553]
        assert list(solver.eval(b / d, 2)) == [0]
        assert list(solver.eval(a % c, 2)) == [2]
        assert list(solver.eval(a % d, 2)) == [5]
        assert list(solver.eval(b % c, 2)) == [2]
        assert list(solver.eval(b % d, 2)) == [2**32-5]

        # test unsigned
        assert list(solver.eval(a.SDiv(c), 2)) == [1]
        assert list(solver.eval(a.SDiv(d), 2)) == [2**32-1]
        assert list(solver.eval(b.SDiv(c), 2)) == [2**32-1]
        assert list(solver.eval(b.SDiv(d), 2)) == [1]
        assert list(solver.eval(a.SMod(c), 2)) == [2]
        assert list(solver.eval(a.SMod(d), 2)) == [2]
        assert list(solver.eval(b.SMod(c), 2)) == [2**32-2]
        assert list(solver.eval(b.SMod(d), 2)) == [2**32-2]

    def test_arith_shift(self):
        bc = claripy.backends.concrete
        a = claripy.BVV(-4, 32)
        assert bc.convert(a >> 1) == -2

        solver = claripy.Solver()
        a = claripy.BVS("a", 32)
        solver.add(a == -4)
        assert list(solver.eval(a >> 1, 2)) == [2**32-2]

    def test_bool_conversion(self):
        a = claripy.BVV(42, 32)
        try:
            assert a == 42
            assert False, "`assert ast` should raise an exception"
        except claripy.ClaripyOperationError:
            pass

        try:
            bool(a == 42)
            assert False, "bool(ast) should raise an exception"
        except claripy.ClaripyOperationError:
            pass

        try:
            if a == 42:
                pass
            assert False, "`if ast` should raise an exception"
        except claripy.ClaripyOperationError:
            pass

if __name__ == '__main__':
    unittest.main()
