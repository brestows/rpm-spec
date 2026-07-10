# nginx source version this module is compiled against. A dynamic module only
# loads into the exact nginx version it was built with, so this tracks whatever
# the target distro ships.
#
# EL9 ships nginx 1.20.1 as a plain package and EL10 ships 1.26.3. EL8 ships
# nginx only as a module stream, defaulting to 1.14 -- which does not even carry
# an nginx(abi) provide -- so the copr chroot needs nginx:1.20 enabled. If it is
# not, %build aborts rather than producing a module nginx refuses to load.
%if 0%{?rhel} >= 10
%global nginx_version 1.26.3
%else
%global nginx_version 1.20.1
%endif

%global modname headers-more
%global moddir  %{_libdir}/nginx/modules
%global soname  ngx_http_headers_more_filter_module.so

# Package name kept as nginx-module-* (not nginx-mod-*) to preserve the upgrade
# path for what is already published in copr.
Name:           nginx-module-headers-more
Version:        0.34
Release:        5%{?dist}
Summary:        headers-more module for nginx
License:        BSD-2-Clause
URL:            https://github.com/openresty/headers-more-nginx-module

# mock unpacks the SRPM into the target chroot and re-runs `rpmbuild -bs` there,
# where %%{rhel} is finally known. Both nginx tarballs therefore have to be in
# the SRPM: listing only the selected one fails the el10 rebuild on a missing
# source, since the SRPM is built once, with %%{rhel} undefined.
Source0:        https://nginx.org/download/nginx-1.20.1.tar.gz
Source1:        https://nginx.org/download/nginx-1.26.3.tar.gz
Source2:        https://github.com/openresty/%{modname}-nginx-module/archive/v%{version}/%{modname}-nginx-module-%{version}.tar.gz
# Upstream ships its licence text only inside the README, so it is carried here.
Source3:        copyright

# nginx is only needed to verify at build time that we compile against the
# version that is actually installed. --with-compat means we do not have to
# replicate the distro's configure flags, so none of its optional deps
# (gd, libxslt, perl, gperftools) are needed here.
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  nginx
BuildRequires:  zlib-devel
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
nginx ngx_headers_more dynamic module. Set and clear input and output headers...
more than "add"!

%prep
%if 0%{?rhel} >= 10
%setup -q -T -b 1 -n nginx-%{nginx_version}
%else
%setup -q -n nginx-%{nginx_version}
%endif
%setup -q -T -D -b 2 -n %{modname}-nginx-module-%{version}
cp -p %{SOURCE3} .

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
    --add-dynamic-module=../%{modname}-nginx-module-%{version}
%make_build modules

%install
install -Dpm 0755 %{_builddir}/nginx-%{nginx_version}/objs/%{soname} \
    %{buildroot}%{moddir}/%{soname}

# The last %%setup left %%{buildsubdir} pointing at the module tree, so %%license
# and %%doc resolve inside it.
%files
%license copyright
%doc README.markdown
%{moddir}/%{soname}

%changelog
* Fri Jul 10 2026 Siarhei Chystsiakou <brestows@gmail.com> - 0.34-5
- Build against --with-compat instead of scraping `nginx -V`, which ran outside
  the buildroot and forced a long list of unrelated BuildRequires
- Pick the nginx version per EL release (8/9/10) and fail early on a mismatch
- Require nginx(abi) rather than an exact nginx NEVR
- Use pcre2-devel on EL9+; EL10 no longer ships PCRE1
- Drop the unused NGINX_COMPILED_FLAGS/BASE_CONFIGURE_ARGS macro block
- Add %%{?dist} to Release

* Fri Jul 01 2022 brestows <brestows@gmail.com> - 0.34-4
- Updated ngx_http_headers_more_filter_module, compiled for nginx 1.20.1

* Wed Jul 01 2020 Dzmitry Stremkouski <mitroko@gmail.com> - 0.33-1.1
- Removing debug libs from main package

* Wed Jun 17 2020 Dzmitry Stremkouski <mitroko@gmail.com> - 0.33-1
- Compiled for nginx base version 1.18.0, module version 0.33
