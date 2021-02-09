/**
 * @file
 * @brief The OP representing the == comparison
 */
#ifndef __OP_EQ_HPP__
#define __OP_EQ_HPP__

#include "binary.hpp"

#include <memory>


// Forward declarations
namespace Expression {
    class Bool;
} // namespace Expression

namespace Op {

    /** The comparison op class: Eq */
    class Eq final : public Binary<> {
        OP_FINAL_INIT(Eq)
      private:
        /** Private constructor */
        explicit inline Eq(const Hash::Hash &h, const Operand &l, const Operand &r)
            : Binary { h, static_cuid, l, r } {}
    };

} // namespace Op

#endif
