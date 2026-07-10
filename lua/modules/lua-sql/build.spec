# EL8 ships Lua 5.3; EL9 and EL10 ship 5.4. Asterisk's pbx_lua links the system
# Lua, so lua(abi) below has to match it exactly -- `lua >= x` would silently
# allow a mismatched ABI.
%if 0%{?rhel} == 8
%global luaver 5.3
%else
%global luaver 5.4
%endif

%global lualibdir %{_libdir}/lua/%{luaver}
%global luapkgdir %{_datadir}/lua/%{luaver}
%global oname     luasql

Name:           lua-sql
Version:        2.6.0
Release:        2%{?dist}
Summary:        Database connectivity for the Lua programming language
License:        MIT
URL:            http://keplerproject.github.io/luasql/
Source0:        https://github.com/lunarmodules/luasql/archive/refs/tags/%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  lua
BuildRequires:  pkgconfig(lua) >= %{luaver}
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  mariadb-devel
# Satisfied by libpq-devel, which carries the Provides on EL8, EL9 and EL10.
BuildRequires:  postgresql-devel


Requires:       %{name}-sqlite = %{version}-%{release}
Requires:       %{name}-mysql = %{version}-%{release}
Requires:       %{name}-postgresql = %{version}-%{release}
Recommends:     %{name}-doc = %{version}-%{release}

%description
LuaSQL is a simple interface from Lua to a DBMS. This package of LuaSQL
supports MySQL, SQLite and PostgreSQL databases. You can execute arbitrary SQL
statements and it allows for retrieving results in a row-by-row cursor fashion.

%files

#------------------------------------------------------------------

%package        doc
Summary:        Documentation for LuaSQL
BuildArch:      noarch

%description    doc
LuaSQL is a simple interface from Lua to a DBMS. This package contains the
documentation for LuaSQL.

%files doc
%doc README doc/us/*

#------------------------------------------------------------------

%package        sqlite
Summary:        SQLite database connectivity for the Lua programming language
Requires:       lua(abi) = %{luaver}

%description    sqlite
LuaSQL is a simple interface from Lua to a DBMS. This package provides access
to SQLite databases.

%files          sqlite
%dir %{lualibdir}/%{oname}
%{lualibdir}/%{oname}/sqlite3.so

#------------------------------------------------------------------

%package        mysql
Summary:        MySQL database connectivity for the Lua programming language
Requires:       lua(abi) = %{luaver}

%description    mysql
LuaSQL is a simple interface from Lua to a DBMS. This package provides access
to MySQL databases.

%files          mysql
%dir %{lualibdir}/%{oname}
%{lualibdir}/%{oname}/mysql.so

#------------------------------------------------------------------

%package        postgresql
Summary:        PostgreSQL database connectivity for the Lua programming language
Requires:       lua(abi) = %{luaver}

%description    postgresql
LuaSQL is a simple interface from Lua to a DBMS. This package provides access
to PostgreSQL databases.

%files          postgresql
%dir %{lualibdir}/%{oname}
%{lualibdir}/%{oname}/postgres.so

#------------------------------------------------------------------

%prep
%setup -q -n %{oname}-%{version}

%build
%make_build DRIVER_INCS="`pkg-config --cflags sqlite3`" DRIVER_LIBS="`pkg-config --libs sqlite3`" DEFS="%{optflags}" sqlite3
%make_build DRIVER_INCS="" DRIVER_LIBS="-lpq" DEFS="%{optflags}" WARN= postgres
%make_build DRIVER_INCS="-I%{_prefix}/include/mysql -I%{_prefix}/include/mysql/server" DRIVER_LIBS="-L%{_libdir}/mysql -lmysqlclient" DEFS="%{optflags}" mysql

%install
%make_install PREFIX=%{buildroot}%{_prefix} LUA_LIBDIR=%{buildroot}%{lualibdir} LUA_DIR=%{buildroot}%{luapkgdir}


# Loading each driver with the system Lua catches an ABI or symbol mismatch that
# a successful compile does not. No server is contacted; only the client library
# is dlopened.
%check
for d in sqlite3 mysql postgres; do
    lua -e "package.cpath = '%{buildroot}%{lualibdir}/?.so;' .. package.cpath
            local drv = require('%{oname}.$d')
            assert(type(drv) == 'table', '$d: module did not return a table')
            assert(type(drv['$d']) == 'function', '$d: no environment constructor')
            io.write('  luasql.$d loads\n')"
done


%changelog
* Fri Jul 10 2026 Siarhei Chystsiakou <brestows@gmail.com> - 2.6.0-2
- Require lua(abi) rather than `lua >= x` in the driver subpackages: Lua breaks
  ABI between minor releases, and Asterisk's pbx_lua loads these against the
  system Lua
- Define luaver for EL10 (5.4); it was only set for EL8 and EL9, which left the
  install paths as /usr/lib64/lua// everywhere else
- Add %%{?dist} to Release, mark the doc subpackage noarch
- Add a %%check that loads each driver with the system Lua
- Drop the commented-out Patch0/autopatch lines and the obsolete Group tags

* Fri Jul 22 2022 Chystsiakou Siarhei 2.3.5-4.el8
+ Revision: 18221120
- rebuild for rocky 8

* Sun Jul 26 2020 daviddavid <daviddavid> 2.3.5-4.mga8
+ Revision: 1609035
- fix build with mariadb 10.5.4

* Thu Feb 13 2020 umeabot <umeabot> 2.3.5-3.mga8
+ Revision: 1514903
- Mageia 8 Mass Rebuild

* Sun Sep 23 2018 umeabot <umeabot> 2.3.5-2.mga7
+ Revision: 1299378
- Mageia 7 Mass Rebuild

* Wed Apr 04 2018 kekepower <kekepower> 2.3.5-1.mga7
+ Revision: 1215169
- Update to version 2.3.5

* Sat Dec 23 2017 wally <wally> 2.3.1-2.mga7
+ Revision: 1184307
- add patch to fix build with new mariadb 10.2
- rebuild for new mariadb

* Mon Mar 28 2016 shlomif <shlomif> 2.3.1-1.mga6
+ Revision: 995989
- New version 2.3.1

* Mon Feb 08 2016 umeabot <umeabot> 2.3.0-6.mga6
+ Revision: 950850
- Mageia 6 Mass Rebuild

* Tue Nov 25 2014 cjw <cjw> 2.3.0-5.mga5
+ Revision: 798917
- rebuild against postgresql9.4

* Wed Oct 15 2014 umeabot <umeabot> 2.3.0-4.mga5
+ Revision: 746251
- Second Mageia 5 Mass Rebuild

* Tue Sep 16 2014 umeabot <umeabot> 2.3.0-3.mga5
+ Revision: 682032
- Mageia 5 Mass Rebuild
+ tv <tv>
- s/uggests:/Recommends:/

* Sun Aug 31 2014 akien <akien> 2.3.0-2.mga5
+ Revision: 669805
- Readd empty %%files for main package acting as a meta-package

* Sun Aug 10 2014 akien <akien> 2.3.0-1.mga5
+ Revision: 661539
- Version 2.3.0

* Fri Oct 18 2013 umeabot <umeabot> 2.1.1-11.mga4
+ Revision: 507605
- Mageia 4 Mass Rebuild

* Sat Jan 12 2013 umeabot <umeabot> 2.1.1-10.mga3
+ Revision: 359072
- Mass Rebuild - https://wiki.mageia.org/en/Feature:Mageia3MassRebuild

* Sun Dec 23 2012 pterjan <pterjan> 2.1.1-9.mga3
+ Revision: 334424
- Force Lua 5.1

* Thu Mar 24 2011 dmorgan <dmorgan> 2.1.1-8.mga1
+ Revision: 77055
- Rebuild against new mysql

* Sun Mar 13 2011 shikamaru <shikamaru> 2.1.1-7.mga1
+ Revision: 70280
- imported package lua-sql


* Sat Mar 12 2011 Rémy Clouard <shikamaru@mandriva.org> 2.1.1-7.mga1
- clean spec (buildroot)

* Sat Jan 01 2011 Oden Eriksson <oeriksson@mandriva.com> 2.1.1-6mdv2011.0
+ Revision: 627256
- rebuilt against mysql-5.5.8 libs, again

* Thu Dec 30 2010 Oden Eriksson <oeriksson@mandriva.com> 2.1.1-5mdv2011.0
+ Revision: 626538
- rebuilt against mysql-5.5.8 libs

* Wed Dec 08 2010 Rémy Clouard <shikamaru@mandriva.org> 2.1.1-3mdv2011.0
+ Revision: 616184
- rebuild for the mass rebuild

* Mon Sep 14 2009 Thierry Vignaud <tv@mandriva.org> 2.1.1-2mdv2010.0
+ Revision: 439656
- rebuild

* Mon Dec 29 2008 Jérôme Soyer <saispo@mandriva.org> 2.1.1-1mdv2009.1
+ Revision: 320764
- Fix RPM Group
- Fix BR
- SPEC Cleanup
- import lua-sql

