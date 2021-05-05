/**
 * @file
 * \ingroup utils
 */
#include "stack_limit.hpp"


// Not all systems support this
#if !__has_include(<sys/resource.h>)


/** A helper function which reports that StackLimit operations are not supported on this system */
static void not_supported() {
    throw Utils::Error::Unexpected::NotSupported(
        WHOAMI_WITH_SOURCE "This system does not support StackLimit operations");
}

unsigned long long Utils::StackLimit::get() {
    not_supported();
}
unsigned long long Utils::StackLimit::max() {
    not_supported();
}
void Utils::StackLimit::set(const unsigned long long) {
    not_supported();
}


// Systems that do support this
#else


    #include "affirm.hpp"
    #include "error.hpp"
    #include "verify_syscall.hpp"

    #include <cerrno>
    #include <cstring>
    #include <sys/resource.h>

/** A helper function to get the current rlimit struct */
static rlimit getr() {
    rlimit rl {};
    const auto rv { getrlimit(RLIMIT_STACK, &rl) };
    Utils::verify_syscall(rv);
    return rl;
}

unsigned long long Utils::StackLimit::get() {
    return getr().rlim_cur;
}

unsigned long long Utils::StackLimit::max() {
    return getr().rlim_max;
}

void Utils::StackLimit::set(const unsigned long long to) {
    auto rl { getr() };
    affirm<Error::Unexpected::IncorrectUsage>(to <= rl.rlim_max, WHOAMI_WITH_SOURCE,
                                              "selected stack limit of ", to,
                                              " is greater than the max of: ", rl.rlim_max);
    rl.rlim_cur = to;
    const auto rv { setrlimit(RLIMIT_STACK, &rl) };
    verify_syscall(rv);
}


#endif
