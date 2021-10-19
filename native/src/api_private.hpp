/**
 * @file
 * @brief This header exposes the private C API for claricpp
 */
#ifndef R_APIPRIVATE_HPP_
#define R_APIPRIVATE_HPP_

extern "C" {
#include "api_public.h"
};
#include "annotation.hpp"
#include "backend.hpp"
#include "create.hpp"
#include "py_obj.hpp"
#include "simplification.hpp"
#include "utils.hpp"

/********************************************************************/
/*                               C++                                */
/********************************************************************/

namespace API {

    namespace Private {
        /** Bidirectionally maps between C++ and C types */
        template <typename T> struct InternalMap;

        /** A local macro used to add a Map entry */
#define MAP_ADD(CTYPE, CPPTYPE)                                                                   \
    static_assert(std::is_pod_v<CTYPE>, "Struct must be of the structure { void * ptr };");       \
    static_assert(sizeof(CTYPE) == sizeof(void *), "Struct should only contain a void *");        \
    static_assert(std::is_same_v<void *, decltype(std::declval<CTYPE>().ptr)>, "Bad ptr type");   \
    static_assert(Utils::is_shared_ptr<CPPTYPE>, "CPPTYPE should be a shared pointer");           \
    template <> struct InternalMap<CPPTYPE> final { using Result = CTYPE; };                      \
    template <> struct InternalMap<CTYPE> final { using Result = CPPTYPE; }

        // Populate InternalMap
        MAP_ADD(ClaricppAnnotation, Annotation::BasePtr);
        MAP_ADD(ClaricppSPAV, Annotation::SPAV);
        MAP_ADD(ClaricppExpr, Expression::BasePtr);

// Cleanup
#undef MAP_ADD

        /** A shortcut used to access InternalMap */
        template <typename T> using Map = typename InternalMap<T>::Result;

        /** Heap cache; key type is in C++ */
        template <typename T> static thread_local Utils::HeapCache<T> cache {};

    } // namespace Private

    /** Returns a pointer to the C++ type held by the C type x */
    template <typename InC> static inline auto *to_cpp_ptr(const InC &x) noexcept {
        UTILS_AFFIRM_NOT_NULL_DEBUG(x.ptr);
        return static_cast<Private::Map<InC> *const>(x.ptr);
    }

    /** Returns a reference to the C++ type held by the C type x
     *  Warning: Returns a reference to part of x
     */
    template <typename InC> static inline auto &to_cpp_ref(const InC &x) noexcept {
        return *to_cpp_ptr(x);
    }

    /** Heap cache function */
    template <typename InCpp> static inline auto to_c(InCpp &&x) {
        return Private::Map<InCpp> { Private::cache<InCpp>.move_to_heap(std::move(x)) };
    }

    /** Heap cache function with emplacement */
    template <typename InCpp, typename... Args> static inline auto emplace_to_c(Args &&...args) {
        return Private::Map<InCpp> { Private::cache<InCpp>.emplace_on_heap(
            std::forward<Args>(args)...) };
    }

    /** Heap cache free function */
    template <typename InC> static inline void free(InC &x) {
        Private::cache<Private::Map<InC>>.free(to_cpp_ptr(x));
        x.ptr = nullptr;
    }

} // namespace API

#endif
