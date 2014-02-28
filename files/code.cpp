#include <iostream>
#include <list>
#include <memory>
#include <vector>
#include <string>
#include <sstream>
#include <ctime>
#include <cstdlib>
#include <cassert>

using namespace std;

#define RANGE(r) (std::begin(r), std::end(r))
int main()
{ int const range = 3500000, samples = 10000; assert(range < RAND_MAX); int x = 0; for (int u = 0; u != samples; ++u) if ((rand() % range) < range / 2) ++x; cout << x / (double)samples * 100 << "% of samples lie in lower half of chosen range"; }