/**
 * @file
 * \ingroup unittest
 */
#include "testlib.hpp"


/** Verify that the Concrete class works */
void literal() {
    // Construct
    Constants::CCSC s = { "hi" };
    const auto c1 = Op::factory<Op::Literal>(s, 2_ui);
    const auto c2 = Op::factory<Op::Literal>(s, 2_ui);
    // Verify factory works
    UNITTEST_ASSERT(c1 == c2)
}

// Define the test
UNITTEST_DEFINE_MAIN_TEST(literal)
