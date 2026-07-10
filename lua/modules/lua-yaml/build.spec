# EL8 ships Lua 5.3; EL9 and EL10 ship 5.4. Asterisk's pbx_lua links the system
# Lua, so lua(abi) below has to match it exactly -- `lua >= x` would silently
# allow a mismatched ABI.
%if 0%{?rhel} == 8
%global luaver 5.3
%else
%global luaver 5.4
%endif

%global lualibdir    %{_libdir}/lua/%{luaver}
%global luamoduledir %{_datadir}/lua/%{luaver}

Name:           lyaml
Version:        6.2.8
Release:        3%{?dist}
Summary:        YAML handling library for Lua

License:        MIT
URL:            https://gvvaughan.github.io/lyaml/
Source0:        https://github.com/gvvaughan/lyaml/archive/refs/tags/v%{version}.tar.gz
Source1:        https://luarocks.org/manifests/gvvaughan/lyaml-%{version}-1.src.rock

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  lua
BuildRequires:  libyaml-devel
BuildRequires:  lua-devel
BuildRequires:  pkgconfig
BuildRequires:  luarocks

Requires:       lua(abi) = %{luaver}

%description
This is a Lua binding for the fast libYAML C library for converting
between %%YAML 1.1 and Lua tables, with a flexible Lua language API to load and
save YAML documents.

%global debug_package %{nil}

%prep
cp -a %{SOURCE1} .
tar xf %{SOURCE0} -C .

%build
mkdir tree
TMP=$PWD/tmp luarocks --local --tree=./tree build lyaml-%{version}-1.src.rock CFLAGS="%{optflags} -fPIC -DLUA_COMPAT_APIINTCASTS" LYAML_LIBDIR=%{_libdir}

%install
install -d %{buildroot}%{lualibdir}
install -d %{buildroot}%{luamoduledir}
cp -P tree/%{_lib}/lua/%{luaver}/* %{buildroot}%{lualibdir}
cp -rP %{name}-%{version}/lib/* %{buildroot}%{luamoduledir}

# lyaml is the pure-Lua half plus a yaml.so binding; loading it with the system
# Lua is the only way to see that the two halves actually fit together.
%check
lua -e "package.cpath = 'tree/%{_lib}/lua/%{luaver}/?.so;' .. package.cpath
        package.path  = '%{name}-%{version}/lib/?.lua;%{name}-%{version}/lib/?/init.lua;' .. package.path
        local lyaml = require('lyaml')
        local t = lyaml.load('a: 1\nb: [x, y]\n')
        assert(t.a == 1, 'load: scalar')
        assert(t.b[2] == 'y', 'load: sequence')
        assert(lyaml.dump({ { k = 'v' } }):find('k: v'), 'dump')
        io.write('  lyaml round-trip ok\n')"

%files
%{lualibdir}/*
%{luamoduledir}/*

%changelog
* Fri Jul 10 2026 Siarhei Chystsiakou <brestows@gmail.com> - 6.2.8-3
- Drop `Provides: libyaml`. lyaml is a Lua binding, not the C library; that
  provide could satisfy another package's dependency on libyaml itself
- Define luaver for EL10 (5.4); it was only set for EL8 and EL9, which left the
  install paths as /usr/lib64/lua// everywhere else
- Take the tarball version from %%{version} instead of hardcoding v6.2.8
- Drop oniguruma-devel and tre-devel, copy-pasted from lua-rex and unused here
- Add a %%check that round-trips a document through the system Lua
- Drop the obsolete Group tag

* Sun May 14 2023 brestows <brestows@gmail.com> - 6.2.8-2
- fix missing files

* Sun May 14 2023 brestows <brestows@gmail.com> - 6.2.8-1
- Update to a latest version
