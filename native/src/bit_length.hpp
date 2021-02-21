/**
 * @file
 * @brief This file defines a class that has a const size
 */
#ifndef __BITLENGTH_HPP__
#define __BITLENGTH_HPP__

#include "constants.hpp"
#include "macros.hpp"


/** A class with a const bit length */
struct BitLength {
  public:
    /** The size */
    const Constants::UInt bit_length;

    /** The number of bits in a byte */
    static inline const constexpr Constants::UInt char_bit { 8_ui };

  protected:
    /** Protected constructor */
    explicit inline BitLength(const Constants::UInt bl) noexcept : bit_length { bl } {}

    /** Virtual destructor */
    virtual inline ~BitLength() noexcept;

    // Rule of 5
    SET_IMPLICITS_CONST_MEMBERS(BitLength, default, noexcept)
};

/** Default virtual destructor */
BitLength::~BitLength() noexcept = default;


#endif
