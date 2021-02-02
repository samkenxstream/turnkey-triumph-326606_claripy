/**
 * @file
 * \ingroup utils
 * @brief This file defines the clog logging backend
 */
#ifndef __UTILS_LOG_BACKEND_CLOG_HPP__
#define __UTILS_LOG_BACKEND_CLOG_HPP__

#include "ostream.hpp"

#include <iostream>


namespace Utils::Log::Backend {

    /** The stream backend
     *  This takes in an ostream and logs to it
     *  When the buffer is flushed is deffered to std::clog
     */
    struct Clog : public OStream {

        /** Constructor */
        inline Clog() : OStream(std::make_shared<std::ostream>(std::clog.rdbuf()), false, false) {}
    };

} // namespace Utils::Log::Backend

#endif
