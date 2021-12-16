/**
 * @file
 * \ingroup util
 */
#include "../../assert_not_null_debug.hpp"
#include "../../thread_safe.hpp"
#include "../log.hpp"


// For brevity
using namespace Util;
using namespace Log;
using Bk = Backend::Base;


// Create a thread safe backend wrapper
static ThreadSafe::Access<const Bk> access {
    make_derived_shared<const Bk, const Backend::Default>()
};

void Backend::unsafe_set(std::shared_ptr<const Base> &&ptr, const bool silent) {
    UTIL_ASSERT_NOT_NULL_DEBUG(ptr);
    if (!silent) {
        info("Replacing log backend \"", get()->name(), "\" with log backend \"", ptr->name(), '"');
    }
    access.set_shared_ptr_move(std::move(ptr));
    if (!silent) {
        info("Log backend successfully installed!");
    }
}

std::shared_ptr<const Backend::Base> Backend::get() {
    return access.get();
}
