/**
 * @file
 * @brief This file defines the base expr
 */
#ifndef R_EXPR_BASE_HPP_
#define R_EXPR_BASE_HPP_

#include "../annotation.hpp"
#include "../factory.hpp"

#include <memory>
#include <sstream>
#include <vector>


// Forward declarations
namespace Op {
    class Base;
    using BasePtr = Factory::Ptr<const Base>;
} // namespace Op

namespace Expr {

    /** The base Expr type
     *  All exprs must subclass this
     */
    class Base : public Factory::FactoryMade {
        FACTORY_ENABLE_CONSTRUCTION_FROM_BASE(Base, 0)
      public:
        /** Return true if and only if this expr is symbolic */
        const bool symbolic;
        /** The Expr Op */
        const Op::BasePtr op;
        /** A set of annotations applied onto this Expr */
        const Annotation::SPAV annotations;

        // Functions

        /** Get the type name */
        virtual inline const char *type_name() const noexcept = 0;
        /** Get the Expr's repr */
        void repr(std::ostream &out) const;
        /** Get the Expr's repr */
        std::string repr() const;

      protected:
        /** Protected Constructor */
        explicit inline Base(const Hash::Hash h, const CUID::CUID &c, const bool sym,
                             Op::BasePtr &&op_, Annotation::SPAV &&sp) noexcept
            : FactoryMade { h, c },
              symbolic { sym },
              op { std::move(op_) },
              annotations { std::move(sp) } {
            Util::affirm<Util::Err::Usage>(op != nullptr, "op may not be nullptr");
#ifdef DEBUG
            ctor_debug_checks();
#endif
        }

        /** Pure virtual destructor */
        inline ~Base() noexcept override = 0;

      private:
        /** Used during debugging for extra checks
         *  These need access to the internals of op so it cannot be inlined
         */
        void ctor_debug_checks() const;

        // Disable other methods of construction
        SET_IMPLICITS_CONST_MEMBERS(Base, delete)
    };

    /** An alias for Factory::Ptr<const Expr::Base> */
    using RawPtr = const Base *;

    /** An alias for Factory::Ptr<const Expr::Base> */
    using BasePtr = Factory::Ptr<const Base>;

    /** Default virtual destructor */
    Base::~Base() noexcept = default;

    /** Overload the << stream operator to use repr */
    inline std::ostream &operator<<(std::ostream &os, const RawPtr &p) {
        p->repr(os);
        return os;
    }

    /** Overload the << stream operator to use repr */
    inline std::ostream &operator<<(std::ostream &os, const BasePtr &p) { return (os << p.get()); }

} // namespace Expr

#endif
