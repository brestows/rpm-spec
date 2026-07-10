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

# lua-nginx-module cannot be built on its own: it depends on the Nginx
# Development Kit, which is not packaged for EL, so NDK is compiled from source
# alongside it and both .so files ship together.
%global ndk_version 0.3.4

# Since ngx_lua 0.10.16 the resty.core Lua library is mandatory: without it on
# the Lua search path nginx aborts at startup. Neither it nor its lrucache
# dependency is packaged for EL, so both are bundled here as plain Lua sources.
#
# resty.core asserts an *exact* ngx_lua version at load time, so these two move
# together: 0.1.32 pairs with ngx_lua 0.10.29. Bumping one without the other
# makes nginx refuse to start. (The pair for 0.10.31 is still a release
# candidate, which is why ngx_lua is held at 0.10.29 here.)
%global restycore_version 0.1.32
%global lrucache_version  0.15

%global moddir  %{_libdir}/nginx/modules
# LuaJIT is Lua 5.1 ABI, and /usr/share/lua/5.1 is on its compiled-in
# package.path. lua-libs owns /usr/share/lua but not the 5.1 subdirectory.
%global lua51dir %{_datadir}/lua/5.1

Name:           nginx-mod-lua
Version:        0.10.29
Release:        1%{?dist}
Summary:        Lua module for nginx
License:        BSD-2-Clause
URL:            https://github.com/openresty/lua-nginx-module

Source0:        https://nginx.org/download/nginx-%{nginx_version}.tar.gz
Source1:        https://github.com/openresty/lua-nginx-module/archive/v%{version}/lua-nginx-module-%{version}.tar.gz
Source2:        https://github.com/vision5/ngx_devel_kit/archive/v%{ndk_version}/ngx_devel_kit-%{ndk_version}.tar.gz
Source3:        https://github.com/openresty/lua-resty-core/archive/v%{restycore_version}/lua-resty-core-%{restycore_version}.tar.gz
Source4:        https://github.com/openresty/lua-resty-lrucache/archive/v%{lrucache_version}/lua-resty-lrucache-%{lrucache_version}.tar.gz

# nginx is only needed to verify at build time that we compile against the
# version that is actually installed. --with-compat means we do not have to
# replicate the distro's configure flags, so none of its optional deps
# (gd, libxslt, perl, gperftools) are needed here.
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  nginx
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
# EPEL. This is the upstream LuaJIT 2.1, not OpenResty's fork; ngx_lua supports
# it, at a performance cost. Plain PUC-Rio Lua has not been supported since
# ngx_lua 0.10.16.
BuildRequires:  pkgconfig(luajit)
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

Provides:       bundled(lua-resty-core) = %{restycore_version}
Provides:       bundled(lua-resty-lrucache) = %{lrucache_version}

%description
ngx_lua embeds LuaJIT into nginx and lets request handling be scripted in Lua.

Alongside ngx_http_lua_module this package ships the Nginx Development Kit
(ndk_http_module), which ngx_lua is built against, and the resty.core Lua
library, which it refuses to start without.

Modules are installed but not enabled. To use them, load NDK first:

    load_module "%{moddir}/ndk_http_module.so";
    load_module "%{moddir}/ngx_http_lua_module.so";

Note that load_module resolves relative paths against nginx's --prefix, not its
--modules-path, so the absolute path above is required.

%prep
%setup -q -n nginx-%{nginx_version}
%setup -q -T -D -b 2 -n ngx_devel_kit-%{ndk_version}
%setup -q -T -D -b 3 -n lua-resty-core-%{restycore_version}
%setup -q -T -D -b 4 -n lua-resty-lrucache-%{lrucache_version}
# Unpacked last so that %%{buildsubdir}, and thus %%license/%%doc, point here.
%setup -q -T -D -b 1 -n lua-nginx-module-%{version}
cp -p ../ngx_devel_kit-%{ndk_version}/LICENSE LICENSE.ndk

%build
installed=$(nginx -v 2>&1 | sed -n 's|^nginx version: nginx/||p')
if [ "$installed" != "%{nginx_version}" ]; then
    echo "This spec builds against nginx %{nginx_version}, but nginx $installed is installed." >&2
    echo "The resulting module would not load. Enable the matching nginx stream," >&2
    echo "or rebuild with --define 'nginx_version $installed'." >&2
    exit 1
fi

# ngx_lua's config script looks these up by environment variable only.
export LUAJIT_INC=$(pkg-config --cflags-only-I luajit | sed -e 's/^-I//' -e 's/ .*//')
export LUAJIT_LIB=$(pkg-config --variable=libdir luajit)

cd %{_builddir}/nginx-%{nginx_version}
./configure \
    --with-compat \
    --with-http_ssl_module \
    --add-dynamic-module=../ngx_devel_kit-%{ndk_version} \
    --add-dynamic-module=../lua-nginx-module-%{version}
%make_build modules

%install
install -Dpm 0755 %{_builddir}/nginx-%{nginx_version}/objs/ndk_http_module.so \
    %{buildroot}%{moddir}/ndk_http_module.so
install -Dpm 0755 %{_builddir}/nginx-%{nginx_version}/objs/ngx_http_lua_module.so \
    %{buildroot}%{moddir}/ngx_http_lua_module.so

# Trailing /. merges into the existing tree: both libraries populate resty/.
install -d %{buildroot}%{lua51dir}
cp -a %{_builddir}/lua-resty-core-%{restycore_version}/lib/. %{buildroot}%{lua51dir}/
cp -a %{_builddir}/lua-resty-lrucache-%{lrucache_version}/lib/. %{buildroot}%{lua51dir}/

%files
%license LICENSE.ndk
%doc README.markdown
%{moddir}/ndk_http_module.so
%{moddir}/ngx_http_lua_module.so
%dir %{lua51dir}
%{lua51dir}/ngx
%{lua51dir}/resty

%changelog
* Fri Jul 10 2026 Siarhei Chystsiakou <brestows@gmail.com> - 0.10.29-1
- Rename from ngx_http_lua_module to nginx-mod-lua, matching its siblings
- Actually build and install ngx_http_lua_module.so: the spec was a copy of
  nginx-mod-headers-more and installed the headers-more .so instead
- Bundle ngx_devel_kit 0.3.4, without which ngx_lua cannot be compiled
- Bundle lua-resty-core 0.1.32 and lua-resty-lrucache 0.15: ngx_lua has refused
  to start without resty.core since 0.10.16, and neither is packaged for EL
- Build against LuaJIT; drop Source2: copyright, which never existed here
- Update to 0.10.29 and build with --with-compat, per EL release (8/9/10)
