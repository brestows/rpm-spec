# EL8 ships Lua 5.3; EL9 and EL10 ship 5.4. Asterisk's pbx_lua links the system
# Lua, so lua(abi) below has to match it exactly -- `lua >= x` would silently
# allow a mismatched ABI.
%if 0%{?rhel} == 8
%global luaver 5.3
%else
%global luaver 5.4
%endif

# EL10 dropped PCRE1 entirely. lrexlib carries a separate pcre2 backend, which
# builds rex_pcre2.so rather than rex_pcre.so -- scripts there must
# `require "rex_pcre2"`. The function API matches; the flag constants do not.
%if 0%{?rhel} >= 10
%global rexpcre pcre2
%else
%global rexpcre pcre
%endif

%global lualibdir %{_libdir}/lua/%{luaver}
# Deliberately a lazy define: an eager global would expand its body here,
# before Version: exists, and substitute into an undefined macro.
%define rel rel-%(echo %{version} |sed 's/\\./-/g')

Name:           lua-rex
Version:        2.9.2
Release:        2%{?dist}
Summary:        Regular expression handling library for Lua

License:        MIT
URL:            https://lrexlib.luaforge.net/
Source0:        https://github.com/rrthomas/lrexlib/archive/%{rel}.tar.gz
# Both PCRE rocks are listed unconditionally. copr builds the SRPM once, with
# %%{rhel} undefined, then mock re-runs `rpmbuild -bs` inside the target chroot
# where the %%if above finally resolves. A conditional Source: would leave the
# el10 rebuild looking for a rock that never made it into the SRPM.
Source1:        https://luarocks.org/repositories/rocks/lrexlib-pcre-%{version}-1.src.rock
Source2:        https://luarocks.org/repositories/rocks/lrexlib-posix-%{version}-1.src.rock
Source3:        https://luarocks.org/repositories/rocks/lrexlib-tre-%{version}-1.src.rock
Source4:        https://luarocks.org/repositories/rocks/lrexlib-oniguruma-%{version}-1.src.rock
Source5:        https://luarocks.org/repositories/rocks/lrexlib-gnu-%{version}-1.src.rock
Source6:        https://luarocks.org/repositories/rocks/lrexlib-pcre2-%{version}-1.src.rock

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  lua
BuildRequires:  chrpath
BuildRequires:  oniguruma-devel
BuildRequires:  lua-devel
BuildRequires:  tre-devel
BuildRequires:  pkgconfig
BuildRequires:  luarocks
%if 0%{?rhel} >= 10
BuildRequires:  pcre2-devel
%else
BuildRequires:  pcre-devel
%endif

Requires:       lua(abi) = %{luaver}
Provides:       lrexlib = %{version}

%description
Lrexlib are bindings of five regular expression library APIs (POSIX, PCRE,
GNU, TRE, and Oniguruma) to Lua.

On EL8 and EL9 the PCRE binding is rex_pcre; on EL10, where PCRE1 no longer
exists, it is rex_pcre2.

%global debug_package %{nil}

%prep
%setup -q -n lrexlib-%{rel}
rm .gitignore doc/.gitignore
cp -a %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE6} .


%build
mkdir tree
for i in %{rexpcre} posix oniguruma tre gnu; do
	TMP=$PWD/tmp luarocks --local --tree=./tree build lrexlib-$i-%{version}-1.src.rock CFLAGS="%{optflags} -fPIC -DLUA_COMPAT_APIINTCASTS" ONIG_LIBDIR=%{_libdir} TRE_LIBDIR=%{_libdir} PCRE_LIBDIR=%{_libdir} PCRE2_LIBDIR=%{_libdir}
done


%install
install -d %{buildroot}%{lualibdir}
# Globbed, because the PCRE binding is named rex_pcre or rex_pcre2 by release.
cp -P tree/%{_lib}/lua/%{luaver}/rex_*.so* %{buildroot}%{lualibdir}

# luarocks bakes -Wl,-rpath,%{_libdir} into every binding it links against a
# named *_LIBDIR. EL10's check-rpaths rejects a standard rpath outright, where
# EL8 and EL9 only warned. Strip it: the loader finds %{_libdir} by itself.
for so in %{buildroot}%{lualibdir}/rex_*.so; do
    chrpath --delete "$so" || :
done


# Upstream's `make test` exercises an in-tree build, which is not what luarocks
# produced. Load each binding with the system Lua instead: that is what Asterisk
# will do, and it catches an ABI or symbol mismatch that a compile would not.
%check
for m in rex_%{rexpcre} rex_posix rex_onig rex_tre rex_gnu; do
    lua -e "package.cpath = 'tree/%{_lib}/lua/%{luaver}/?.so;' .. package.cpath
            local rex = require('$m')
            assert(rex._VERSION, '$m: no _VERSION')
            assert(rex.match('abc', 'a.c') == 'abc', '$m: match failed')
            io.write('  ', '$m', ' -> ', rex._VERSION, '\\n')"
done


%files
%{lualibdir}/*
%doc ChangeLog.old NEWS README.rst doc
%license LICENSE


%changelog
* Fri Jul 10 2026 Siarhei Chystsiakou <brestows@gmail.com> - 2.9.2-2
- Define luaver for EL10 (5.4); it was only set for EL8 and EL9, which left
  the install paths as /usr/lib64/lua// everywhere else
- Build the pcre2 binding on EL10, which no longer ships PCRE1. Both rocks are
  now unconditional Sources, since copr resolves %%if only when mock re-runs
  rpmbuild -bs inside the chroot
- Replace %%check: instead of upstream's in-tree `make test`, load every built
  binding with the system Lua, which is how Asterisk will load it
- Strip the rpath luarocks bakes in; EL10's check-rpaths treats a standard
  rpath as an error rather than a warning
- Drop the obsolete Group tag

* Sat Feb 24 2024 Siarhei Chystsiakou <brestows@gmail.com> - 2.9.2-1
- Update to a latest version

* Tue Aug 29 2017 Lubomir Rintel <lkundrak@v3.sk> - 2.8.0-1
- Update to a latest version

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Oct 30 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.7.2-13
- Rebuild for oniguruma 6.1.1

* Mon Jul 18 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.7.2-12
- Rebuild for oniguruma 6

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu May 14 2015 Ville Skytt√§ <ville.skytta@iki.fi> - 2.7.2-9
- Mark LICENSE as %%license, don't ship .gitignore

* Thu Jan 15 2015 Tom Callaway <spot@fedoraproject.org> - 2.7.2-8
- rebuild for lua 5.3

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Oct 24 2013 Lubomir Rintel <lkundrak@v3.sk> - 2.7.2-5
- Bulk sad and useless attempt at consistent SPEC file formatting

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun  4 2013 Tom Callaway <spot@fedoraproject.org>	- 2.7.2-3
- use lua(abi) for Requires. A B I.

* Mon Jun  3 2013 Tom Callaway <spot@fedoraproject.org> - 2.7.2-2
- use lua(api) for Requires

* Sun May 12 2013 Tom Callaway <spot@fedoraproject.org> - 2.7.2-1
- update to 2.7.2

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 2.4.0-8
- Rebuild against PCRE 8.30

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 23 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.4.0-3
- Compile shared library as PIC

* Wed Dec 17 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.4.0-2
- Add doc directory to documentation
- Allow parallel make runs

* Tue Dec 16 2008 Lubomir Rintel <lkundrak@v3.sk> - 2.4.0-1
- Initial packaging
