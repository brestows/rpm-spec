# nginx source version this module is compiled against.
# A dynamic module only loads into the exact nginx version it was built with,
# so this has to track whatever the target distro ships. Override on the
# command line with: rpmbuild --define 'nginx_version 1.24.0'
#
# EL9 ships nginx 1.20.1 as a plain package and EL10 ships 1.26.3. EL8 ships
# nginx only as a module stream, defaulting to 1.14 -- which does not even carry
# an nginx(abi) provide -- so the copr chroot needs nginx:1.20 enabled. If it is
# not, %build aborts rather than producing a module nginx refuses to load.
%if %{undefined nginx_version}
%global nginx_version 1.20.1
%if 0%{?rhel} >= 10
%global nginx_version 1.26.3
%endif
%endif

%global modname geoip2
%global moddir  %{_libdir}/nginx/modules

Name:           nginx-mod-geoip2
Version:        3.4
Release:        3%{?dist}
Summary:        GeoIP2 module for nginx
License:        BSD-2-Clause
URL:            https://github.com/leev/ngx_http_geoip2_module

Source0:        https://nginx.org/download/nginx-%{nginx_version}.tar.gz
Source1:        https://github.com/leev/ngx_http_geoip2_module/archive/%{version}/%{modname}-%{version}.tar.gz

# nginx is only needed to verify at build time that we compile against the
# version that is actually installed. --with-compat means we do not have to
# replicate the distro's configure flags, so none of its optional deps
# (gd, libxslt, perl, gperftools) are needed here.
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  nginx
BuildRequires:  zlib-devel
BuildRequires:  libmaxminddb-devel
# nginx switched to PCRE2 in 1.21.5, so 1.20.1 needs PCRE1. Both are pulled in
# where both exist, so an overridden nginx_version still finds its headers.
# EL10 dropped PCRE1 altogether.
%if 0%{?rhel} >= 10
BuildRequires:  pcre2-devel
%else
BuildRequires:  pcre-devel
BuildRequires:  pcre2-devel
%endif

Requires:       nginx(abi) = %{nginx_version}

%description
GeoIP2 module for nginx. Looks up the geographic location of a client address
in a MaxMind GeoIP2 (.mmdb) database and exposes the result as nginx variables.

%prep
%setup -q -n nginx-%{nginx_version}
%setup -q -T -D -b 1 -n ngx_http_%{modname}_module-%{version}

%build
installed=$(nginx -v 2>&1 | sed -n 's|^nginx version: nginx/||p')
if [ "$installed" != "%{nginx_version}" ]; then
    echo "This spec builds against nginx %{nginx_version}, but nginx $installed is installed." >&2
    echo "The resulting module would not load. Enable the matching nginx stream," >&2
    echo "or rebuild with --define 'nginx_version $installed'." >&2
    exit 1
fi

cd %{_builddir}/nginx-%{nginx_version}
./configure \
    --with-compat \
    --add-dynamic-module=../ngx_http_%{modname}_module-%{version}
%make_build modules

%install
install -Dpm 0755 %{_builddir}/nginx-%{nginx_version}/objs/ngx_http_%{modname}_module.so \
    %{buildroot}%{moddir}/ngx_http_%{modname}_module.so

# The last %%setup left %%{buildsubdir} pointing at the module tree, so %%license
# and %%doc resolve inside it.
%files
%license LICENSE
%doc README.md
%{moddir}/ngx_http_%{modname}_module.so

%changelog
* Fri Jul 10 2026 Siarhei Chystsiakou <brestows@gmail.com> - 3.4-3
- Build against --with-compat instead of scraping `nginx -V`, which ran outside
  the buildroot and forced a long list of unrelated BuildRequires
- Pick the nginx version per EL release (8/9/10) and fail early on a mismatch
- Require nginx(abi) rather than an exact nginx NEVR
- Use pcre2-devel on EL9+; EL10 no longer ships PCRE1

* Mon Jan 23 2023 brestows <brestows@gmail.com> - 3.4-2
- Compiled for nginx base version 1.20.1
