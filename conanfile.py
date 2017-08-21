from conans import ConanFile, CMake, tools
import os
import re


class PcreConan(ConanFile):
    name = "pcre"
    version = "8.40.0"
    license = "MIT"
    url = "https://github.com/kmaragon/conan-pcre"
    settings = "os", "compiler", "build_type", "arch"
    description = "pcre[1] package"
    default_options = "shared=False"
    generators = "cmake"
    requires = "bzip2/[~=1.0.6]@lasote/stable","zlib/[~=1.2.8]@lasote/stable"
    exports = "CMakeLists.txt"
    
    options = {
        "shared": [True, False],
        "enablecpp": [True, False],
        "enableutf": [True, False]
    }
    
    default_options = "shared=True","enablecpp=True","enableutf=True"

    def source(self):
        version = self.version[0:self.version.rfind('.')]
        tools.download("http://ftp.pcre.org/pub/pcre/pcre-%s.tar.gz" % version, "pcre.tar.gz")

        tools.untargz("pcre.tar.gz")
        os.unlink("pcre.tar.gz")

    def build(self):
        cmake = CMake(self.settings)
        finished_package = os.getcwd() + "/pkg"

        make_options = os.getenv("MAKEOPTS") or ""
        if not re.match("/[^A-z-a-z_-]-j", make_options):
            cpucount = tools.cpu_count()
            make_options += " -j %s" % (cpucount * 2)

        # cmake
        self.run('mkdir -p pkg && mkdir -p build')
        self.run('cd build && cmake %s -DCMAKE_SKIP_BUILD_RPATH=FALSE ' % cmake.command_line +
                '-DBUILD_SHARED_LIBS:BOOL=%s' % ("TRUE" if self.options.shared else "FALSE") +
                ' -DPCRE_SUPPORT_UTF:BOOL=%s' % ("TRUE" if self.options.enableutf else "FALSE") +
            ' -DCMAKE_BUILD_WITH_INSTALL_RPATH=TRUE -DCMAKE_INSTALL_RPATH="%s/lib"' % finished_package +
            ' -DCMAKE_INSTALL_PREFIX:PATH="%s" -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=TRUE -f ../' % finished_package)

        # build
        self.run("cd build && make %s install" % make_options)

    def package(self):
        self.copy("*", dst="lib", src="pkg/lib")
        self.copy("*", dst="bin", src="pkg/bin")
        self.copy("*", dst="include", src="pkg/include")

    def package_info(self):
        if self.options.shared:
	    if self.options.enablecpp:
               self.cpp_info.libs = ["pcre", "pcrecpp"]
            else:
               self.cpp_info.libs = ["pcre"]
        else:
            self.cpp_info.libs = ["libpcre.a"]
	    if self.options.enablecpp:
               self.cpp_info.libs = ["libpcrecpp.a"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
