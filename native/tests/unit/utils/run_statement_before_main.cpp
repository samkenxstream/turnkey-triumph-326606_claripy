/**
 * @file
 * \ingroup unittest
 */
#include "testlib.hpp"
#include "utils.hpp"


/** A global variable */
int i = 0;

// Run i = 4 before main
UTILS_RUN_STATEMENT_BEFORE_MAIN(i = 4);


/** Ensure f(4) was run before main */
int run_statement_before_main() {
    UNITTEST_ASSERT(i == 4)
    return 0;
}
