// Host-only metadata probe. Links the owner's local WinVita PeImage loader.
// Does not resolve imports, start a CPU, or execute any guest instruction.
#include "runtime/pe_image.h"
#include <fstream>
#include <iostream>
#include <iterator>
#include <map>
#include <set>
#include <vector>

int main(int argc, char** argv) {
    if (argc != 2) return 2;
    std::ifstream input(argv[1], std::ios::binary);
    if (!input) return 2;
    std::vector<uint8_t> bytes{std::istreambuf_iterator<char>(input), {}};
    d2rt::PeImage image;
    std::string error;
    if (!image.load(bytes, 0, error)) {
        std::cerr << "LOAD_FAIL " << error << '\n';
        return 1;
    }
    std::set<std::pair<std::string, std::string>> unique;
    std::map<std::string, unsigned> entries;
    for (const auto& entry : image.imports()) {
        unique.insert({entry.dll, entry.name});
        ++entries[entry.dll];
    }
    std::cout << "LOAD_PASS file_bytes=" << bytes.size()
              << " image_bytes=" << image.image_size()
              << " entry_va=0x" << std::hex << image.entry_va() << std::dec
              << " import_entries=" << image.imports().size()
              << " unique_imports=" << unique.size() << '\n';
    for (const auto& entry : entries)
        std::cout << entry.first << '\t' << entry.second << '\n';
    std::cout << "NO_GUEST_EXECUTION\n";
    return 0;
}
