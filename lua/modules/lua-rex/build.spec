%if 0%{?rhel} == 8
%define luaver 5.3
%endif
%if 0%{?rhel} == 9
%define luaver 5.4
%endif

%define lualibdir %{_libdir}/lua/%{luaver}
%define rel rel-%(echo %{version} |sed 's/\\./-/g')

Name:           lua-rex
Version:        2.9.2
Release:        1%{?dist}
Summary:        Regular expression handling library for Lua

Group:          Development/Libraries
License:        MIT
URL:            https://lrexlib.luaforge.net/
Source0:	https://github.com/rrthomas/lrexlib/archive/%{rel}.tar.gz
Source1:	https://luarocks.org/repositories/rocks/lrexlib-pcre-%{version}-1.src.rock
Source2:	https://luarocks.org/repositories/rocks/lrexlib-posix-%{version}-1.src.rock
Source3:	https://luarocks.org/repositories/rocks/lrexlib-tre-%{version}-1.src.rock
Source4:	https://luarocks.org/repositories/rocks/lrexlib-oniguruma-%{version}-1.src.rock
Source5:	https://luarocks.org/repositories/rocks/lrexlib-gnu-%{version}-1.src.rock

BuildRequires:  oniguruma-devel
BuildRequires:  pcre-devel
BuildRequires:  lua-devel
BuildRequires:	tre-devel
BuildRequires:  pkgconfig
BuildRequires:	luarocks
Requires:       lua(abi) = %{luaver}
Provides:       lrexlib = %{version}

%description
Lrexlib are bindings of five regular expression library APIs (POSIX, PCRE
GNU, TRE, and Oniguruma) to Lua.

%global debug_package %{nil}

%prep
%setup -q -n lrexlib-%{rel}
rm .gitignore doc/.gitignore
cp -a %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} .


%build
mkdir tree
for i in pcre posix oniguruma tre gnu; do
	TMP=$PWD/tmp luarocks --local --tree=./tree build lrexlib-$i-%{version}-1.src.rock CFLAGS="%{optflags} -fPIC -DLUA_COMPAT_APIINTCASTS" ONIG_LIBDIR=%{_libdir} TRE_LIBDIR=%{_libdir} PCRE_LIBDIR=%{_libdir}
done


%install
install -d %{buildroot}%{lualibdir}
cp -P tree/%{_lib}/lua/%{luaver}/rex_{gnu,onig,pcre,posix,tre}.so* %{buildroot}%{lualibdir}


%check
make %{?_smp_mflags} test


%files
%{lualibdir}/*
%doc ChangeLog.old NEWS README.rst doc
%license LICENSE


%changelog
* Tue Feb 24 2024 Siarhei Chystsiakou <brestows@gmail.com> - 2.9.2-1
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
