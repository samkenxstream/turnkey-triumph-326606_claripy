/**
 * @file
 * \ingroup utils
 * @brief This file contains the base claricpp exception
 * These exceptions have python analogs and must be caught and sent to python
 * via a different method.
 */
#ifndef R_UTILS_ERROR_CLARICPP_HPP_
#define R_UTILS_ERROR_CLARICPP_HPP_

#include "../../macros.hpp"
#include "../to_str.hpp"

#include <exception>
#include <string>


namespace Utils::Error {

    /** The base claricpp exception class
     *  Any exception thrown intentioanlly must subclass this
     *  Note: Since exceptions do not need to be super fast and since we have const date members:
     *  for clarity we ignore the rule of 5 in favor of what the compiler defaults. Subclasses
     *  of Claricpp should feel free to do the same unless they have non-const data members
     */
    class Claricpp : public std::exception {
      public:
        /** Constructor: This constructor consumes its arguments via const reference */
        template <typename... Args>
        explicit Claricpp(const Args &...args) : msg(Utils::to_str(args...)) {}

        // Rule of 5 (note that std::string is not noexcept constructible)
        SET_IMPLICITS_CONST_MEMBERS(Claricpp, default, noexcept);

        /** Default virtual destructor */
        ~Claricpp() noexcept override = default;

        /** Message getter */
        [[nodiscard]] inline const char *what() const noexcept override final {
            return msg.c_str();
        }

      private:
        /** The message */
        const std::string msg;

        /** Allow all error factories friend access */
        template <typename T, typename S> friend T factory(const S msg);
    };

} // namespace Utils::Error

#endif
