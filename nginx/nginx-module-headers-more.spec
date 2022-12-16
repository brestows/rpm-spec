#
%if 0%{?rhel} || 0%{?amzn} || 0%{?fedora}
%define _group System Environment/Daemons
BuildRequires: openssl-devel
%endif

%if 0%{?suse_version} >= 1315
%define _group Productivity/Networking/Web/Servers
BuildRequires: libopenssl-devel
%define _debugsource_template %{nil}
%endif

%if 0%{?rhel} == 7
%define epoch 1
Epoch: %{epoch}
%define dist .el7
%endif

%if 0%{?rhel} == 8
%define epoch 1
Epoch: %{epoch}
%define dist .el8
%define _debugsource_template %{nil}
%endif

%if 0%{?fedora}
%define _debugsource_template %{nil}
%global _hardened_build 1
%endif

%define base_version 1.20.1
%define base_release 1%{?dist}.ngx
%define dmod_version 0.33

%define bdir %{_builddir}/%{name}-%{base_version}_%{dmod_version}

Summary: nginx headers-more dynamic module
Name: nginx-module-headers-more
Version: %{base_version}_%{dmod_version}
Release: 1.1%{?dist}.stremki
Vendor: OpenResty, Inc.
URL: https://github.com/openresty/headers-more-nginx-module
Group: %{_group}

Source0: https://nginx.org/download/nginx-%{base_version}.tar.gz
Source1: https://github.com/openresty/headers-more-nginx-module/archive/v%{dmod_version}.tar.gz
Source2: COPYRIGHT_ngx_headers_more


License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{base_version}-%{base_release}-root
BuildRequires: zlib-devel
BuildRequires: pcre-devel
BuildRequires: nginx == %{?epoch:%{epoch}:}%{base_version}-%{base_release}
Requires: nginx == %{?epoch:%{epoch}:}%{base_version}-%{base_release}

%description
nginx ngx_headers_more dynamic module. Set and clear input and output headers...
more than "add"!

%if 0%{?suse_version} || 0%{?amzn}
%debug_package
%endif

%define NGINX_COMPILED_FLAGS $(nginx -V 2>&1 | grep ^config | cut -c22-)
%define BASE_CONFIGURE_ARGS $(echo "%{NGINX_COMPILED_FLAGS}" | sed 's/--with-cc-opt=.*//; s/--with-ld-opt=.*//')
%define WITH_CC_OPT $(echo "%{NGINX_COMPILED_FLAGS}" | grep -Eo \"\\\--with-cc-opt='[^']+'\" | tr -d "'" | cut -c15-)
%define WITH_LD_OPT $(echo "%{NGINX_COMPILED_FLAGS}" | grep -Eo \"\\\--with-ld-opt='[^']+'\" | tr -d "'" | cut -c15-)
%define MODULE_CONFIGURE_ARGS $(echo "--add-dynamic-module=modules/nginx-module-headers-more")

%prep
%setup -qcTn %{name}-%{base_version}_%{dmod_version}
tar --strip-components=1 -zxf %{SOURCE0}
mkdir -p modules/%{name}
cd modules/%{name}
tar --strip-components=1 -zxf %{SOURCE1}
cd ../../


%build

cd %{bdir}

echo "BASE_CONFIGURE_ARGS: %{BASE_CONFIGURE_ARGS}"
echo "MODULE_CONFIGURE_ARGS: %{MODULE_CONFIGURE_ARGS}"
echo "WITH_CC_OPT: %{WITH_CC_OPT}"
echo "WITH_LD_OPT: %{WITH_LD_OPT}"

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
        --with-cc-opt="%{WITH_CC_OPT} " \
        --with-ld-opt="%{WITH_LD_OPT} " \
        --with-debug
make -f objs/Makefile %{?_smp_mflags} modules

for so in `find %{bdir}/objs/ -type f -name "*.so"`; do
    debugso=`echo $so | sed -e "s|.so|-debug.so|"`
    mv $so $debugso
done

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
        --with-cc-opt="%{WITH_CC_OPT} " \
        --with-ld-opt="%{WITH_LD_OPT} "
make -f objs/Makefile %{?_smp_mflags} modules

%install
cd %{bdir}
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-headers-more
%{__install} -m 644 -p %{SOURCE2} \
    $RPM_BUILD_ROOT%{_datadir}/doc/nginx-module-headers-more/COPYRIGHT

%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/nginx/modules
find %{bdir}/objs/ -type f -name "*-debug.so" -delete
for so in `find %{bdir}/objs/ -maxdepth 1 -type f -name "*.so"`; do
    %{__install} -m755 $so $RPM_BUILD_ROOT%{_libdir}/nginx/modules/
done

%check
%{__rm} -rf $RPM_BUILD_ROOT/usr/src
cd %{bdir}
grep -v 'usr/src' debugfiles.list > debugfiles.list.new && mv debugfiles.list.new debugfiles.list
cat /dev/null > debugsources.list
%if 0%{?suse_version} >= 1500
cat /dev/null > debugsourcefiles.list
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_libdir}/nginx/modules/*
%dir %{_datadir}/doc/nginx-module-headers-more
%{_datadir}/doc/nginx-module-headers-more/*


%post
if [ $1 -eq 1 ]; then
cat <<BANNER
----------------------------------------------------------------------

The headers_more dynamic module for nginx has been installed.
To enable this module, add the following to /etc/nginx/nginx.conf
and reload nginx:

    load_module /etc/nginx/modules/ngx_http_headers_more_filter_module.so;

Please refer to the module documentation for further details:
https://github.com/openresty/headers-more-nginx-module#name

----------------------------------------------------------------------
BANNER
fi

%changelog
* Wed Jul 1 2020 Dzmitry Stremkouski <mitroko@gmail.com> - 0.33-1.1
- Removing debug libs from main package

* Wed Jun 17 2020 Dzmitry Stremkouski <mitroko@gmail.com> - 0.33-1
- Compiled for nginx base version 1.18.0, module version 0.33