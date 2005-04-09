#include <iostream>
#include <stdlib.h>

using namespace std;

unsigned long fib(unsigned long n) {
    if (n < 2)
	return(1);
    else
	return(fib(n-2) + fib(n-1));
}

int main(int argc, char *argv[]) {
    cout << fib(32) << endl;
    return 0;
}
