#include <csignal>
#include <iostream>
#include <list>
#include <memory>
#include <vector>
#include <string>
#include <sstream>
#include <ctime>
#include <cmath>
#include <cassert>
#include <cstdlib>
#include <cstdio>
#include <vector>
#include <list>
#include <fstream>
#include <algorithm>
#include <numeric>
#include <iterator>
#include <functional>
#include <ctime>
#include <chrono>
#include <initializer_list>
#include <tuple>
#include <memory>
#include <limits>
#include <exception>
#include <cassert>
#include <array>
#include <deque>
#include <forward_list>
#include <set>
#include <map>
#include <unordered_set>
#include <unordered_map>
#include <stack>
#include <queue>
#include <complex>
#include <valarray>
#include <random>
#include <ratio>
#include <cfenv>
#include <ios>
#include <iomanip>
#include <sstream>
#include <locale>
#include <clocale>
#include <regex>
#include <atomic>
#include <thread>
#include <mutex>
#include <future>
#include <condition_variable>
#include <utility>
#include <experimental/optional>
//#include <experimental/memory_resource>
//#include <experimental/algorithm>
//#include <experimental/numeric>
//#include <experimental/execution_policy>
//#include <experimental/>
//#define GLM_SWIZZLE
#include <glm/glm.hpp>
#include <glm/ext.hpp>




using namespace std;
using namespace glm;

#define RANGE(r) std::begin(r), std::end(r)

namespace cee {
struct bin_proxy {
    explicit bin_proxy(std::ostream & os):os(os){}

    template<typename Rhs>
    friend std::ostream &operator<<(bin_proxy const &b, Rhs const &rhs) {
        return b.os << rhs;
    }

    friend std::ostream &operator<<(bin_proxy const &b, uint8_t const &rhs) {
        return b.os << bitset<8>(rhs);
    }
    friend std::ostream &operator<<(bin_proxy const &b, int8_t const &rhs) {
        return b.os << bitset<8>(rhs);
    }

    friend std::ostream &operator<<(bin_proxy const &b, uint16_t const &rhs) {
        return b.os << bitset<16>(rhs);
    }
    friend std::ostream &operator<<(bin_proxy const &b, int16_t const &rhs) {
        return b.os << bitset<16>(rhs);
    }

    friend std::ostream &operator<<(bin_proxy const &b, uint32_t const &rhs) {
        return b.os << bitset<32>(rhs);
    }
    friend std::ostream &operator<<(bin_proxy const &b, int32_t const &rhs) {
        return b.os << bitset<32>(rhs);
    }

    friend std::ostream &operator<<(bin_proxy const &b, uint64_t const &rhs) {
        return b.os << bitset<64>(rhs);
    }
    friend std::ostream &operator<<(bin_proxy const &b, int64_t const &rhs) {
        return b.os << bitset<64>(rhs);
    }




private:
    std::ostream &os;
};

struct bin_creator { } bin;
bin_proxy operator<<(std::ostream &os, bin_creator) {
    return bin_proxy(os);
}
}
