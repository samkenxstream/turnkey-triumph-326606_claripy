/**
 * @file
 * @brief This file defines a type that can be constructed by factory
 */
#ifndef R_FACTORY_FACTORYMADE_HPP_
#define R_FACTORY_FACTORYMADE_HPP_

#include "private/has_static_cuid.hpp"

#include "../cuid.hpp"
#include "../hash.hpp"
#include "../utils.hpp"

#include <type_traits>


/** Allow factory to construct a class
 *  BASE is the same base class as factory's template Base argument
 *  Factory made subclasses that want to be directly constructed by factory must define this
 *  Leaves class in a private access state
 *  X can be anything, but must be different between different templates of the same class
 *  For example, Foo<int> must give a different X from Foo<bool>
 */
#define FACTORY_ENABLE_CONSTRUCTION_FROM_BASE(BASE, X)                                            \
    /* The CUID does not need to be used in non-instantiated classes */                           \
    CUID_DEFINE_MAYBE_UNUSED((X))                                                                 \
  private:                                                                                        \
    /** Allow verification to have friend access */                                               \
    template <typename, typename...> friend class ::Utils::HasConstructor;                        \
    /** Allow cache friend access for factory construction */                                     \
    friend class ::Utils::WeakCache<Hash::Hash, const BASE>;


namespace Factory {

    /** A type that can be constructed by the factory
     *  All factory constructable types must subclass this
     *  All subclasses that are or have an instantiable subclass constructed via factory
     *	  1. Must include the FACTORY_ENABLE_CONSTRUCTION_FROM_BASE method. Note that
     *		 this also defines a static_cuid
     */
    struct FactoryMade : public Hash::Hashed, public CUID::HasCUID {

        /** Constructor */
        explicit inline FactoryMade(const Hash::Hash &h, const CUID::CUID &c) noexcept
            : Hashed { h }, HasCUID { c } {}

        /** Statically check if Base and T can be factor constructed
         *  Warning: This is not a gaurntee that these types can be factory constructed
         *  It just does a few useful static checks to help with the compiler error messages
         */
        template <typename Base, typename T, typename... Args>
        [[gnu::always_inline]] static constexpr void static_type_check() noexcept {
            // Inheretence
            static_assert(Utils::is_ancestor<FactoryMade, Base>,
                          "Base must derive from FactoryMade");
            static_assert(Utils::is_ancestor<Base, T>,
                          "T must derive from Base"); // Allow equality
            // Verify static_cuid
            static_assert(Private::has_static_cuid<T>,
                          "Factory cannot construct anything without a static_cuid");
            static_assert(Utils::is_exactly_same<const CUID::CUID, decltype(T::static_cuid)>,
                          "T::static_cuid must be of type const CUID::CUID");
            // Constructor
            // Note: We use has_constructor to pass if the desired constructor is private
            static_assert(Utils::has_constructor<T, const Hash::Hash &, Args &&...>,
                          "T does not have a constructor T(const Hash::Hash &, Args...");
        }

      protected:
        /** Pure virtual destructor */
        inline ~FactoryMade() noexcept override = 0;

        // Rule of 5
        DEFINE_IMPLICITS_CONST_MEMBERS_ALL_NOEXCEPT(FactoryMade);
    };

    /** Default virtual destructor */
    FactoryMade::~FactoryMade() noexcept = default;

} // namespace Factory

#endif
