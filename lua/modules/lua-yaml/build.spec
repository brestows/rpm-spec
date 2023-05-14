%define luaver 5.3
%define lualibdir %{_libdir}/lua/%{luaver}

Name:           lua-yaml
Version:        6.2.8
Release:        1%{?dist}
Summary:        YAML handling library for Lua

Group:          Development/Libraries
License:        MIT
URL:            https://gvvaughan.github.io/lyaml/
Source0:	    https://github.com/gvvaughan/lyaml/archive/refs/tags/v6.2.8.tar.gz
Source1:	    https://luarocks.org/manifests/gvvaughan/lyaml-%{version}-1.src.rock

BuildRequires:  oniguruma-devel
BuildRequires:  libyaml-devel
BuildRequires:  lua-devel
BuildRequires:	tre-devel
BuildRequires:  pkgconfig
BuildRequires:	luarocks
Requires:       lua(abi) = %{luaver}
Provides:       libyaml = %{version}

%description
This is a Lua binding for the fast libYAML C library for converting
between %YAML 1.1 and Lua tables, with a flexible Lua language API to load and save YAML documents.

%global debug_package %{nil}

%prep
%setup -q -n lrexlib-%{rel}
rm .gitignore doc/.gitignore
cp -a %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} .


%build
mkdir tree
TMP=$PWD/tmp luarocks --local --tree=./tree build lyaml-%{version}-1.src.rock CFLAGS="%{optflags} -fPIC -DLUA_COMPAT_APIINTCASTS" LYAML_LIBDIR=%{_libdir}



%install
install -d %{buildroot}%{lualibdir}
pwd
ls -la .
cp -P tree/%{_lib}/lua/%{luaver}/lyaml.so* %{buildroot}%{lualibdir}


%check
make %{?_smp_mflags} test


%files
%{lualibdir}/*
%doc ChangeLog.old NEWS README.rst doc
%license LICENSE


%changelog
* Sun May 14 2023 brestows - 6.2.8-1
- Update to a latest version