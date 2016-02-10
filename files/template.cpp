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
//#include <glm/gtc/half_float.hpp>

#include <cxxabi.h>



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

std::ostream &operator<<(std::ostream &os, const std::type_info &info) {
	int tmp;
	char *data = abi::__cxa_demangle(info.name(), 0, 0, &tmp);
	os << data;
	free(data);
	return os;
}

namespace cee
{
class probe
{
    static int32_t nextInstanceNumber;
    public:
    probe(): id("-"), instanceNumber(nextInstanceNumber++)
    {
        print("C");
    }
    probe(std::string _id): id(std::move(_id)), instanceNumber(nextInstanceNumber++)
    {
        print("C");
    }
    
    probe(const probe& other): id(other.id), instanceNumber(nextInstanceNumber++)
    {   
        print("CC");
    }   
    
    probe(probe&& other): id(other.id), instanceNumber(nextInstanceNumber++)
    {   
        other.id = "-";
        print("MC");
    }   

    probe& operator=(const probe& other)
    {   
        id = other.id;
        print("A");
        return *this;
    }   

    probe& operator=(probe&& other)
    {   
        id = other.id;
        other.id = "-";
        print("MA");
        return *this;
    }   
    
    ~probe()
    {   
        print("D");
    }   
    
    private:
    void print(const std::string& action)
    {   
        std::cout << action << ":" << id << "#" << instanceNumber << " ";
    }   

    std::string id; 
    int32_t instanceNumber;
};

int32_t probe::nextInstanceNumber = 0;
}

