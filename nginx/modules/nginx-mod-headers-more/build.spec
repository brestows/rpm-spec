Summary: headers-more module for nginx
Name: nginx-module-headers-more
Version: 0.33
Release: 3
Vendor: OpenResty, Inc.
URL: https://github.com/openresty/headers-more-nginx-module

%define _modname            headers-more
%define _modver             0.34
%define _nginxver           1.20.1
%define nginx_config_dir    %{_sysconfdir}/nginx
%define nginx_build_dir     %{_builddir}/nginx-%{_nginxver}

Source0: https://nginx.org/download/nginx-%{_nginxver}.tar.gz
Source1: https://github.com/openresty/headers-more-nginx-module/archive/v%{_modver}.tar.gz
Source2: copyright

Requires: nginx = 1:%{_nginxver}
BuildRequires: zlib-devel
BuildRequires: pcre-devel
BuildRequires: nginx
BuildRequires: openssl-devel
BuildRequires: libtool
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: openssl-devel
BuildRequires: perl-devel
BuildRequires: gd-devel
BuildRequires: libmaxminddb-devel
BuildRequires: libxslt-devel
BuildRequires: perl-devel
BuildRequires: perl(ExtUtils::Embed)
BuildRequires: gperftools-devel

License: 2-clause BSD-like license

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root


%description
nginx ngx_headers_more dynamic module. Set and clear input and output headers...
more than "add"!


%define NGINX_COMPILED_FLAGS $(nginx -V 2>&1 | grep ^config | cut -c22-)
%define BASE_CONFIGURE_ARGS $(echo "%{NGINX_COMPILED_FLAGS}" | sed 's/--with-cc-opt=.*//; s/--with-ld-opt=.*//')
%define WITH_CC_OPT $(echo "%{NGINX_COMPILED_FLAGS}" | grep -Eo \"\\\--with-cc-opt='[^']+'\" | tr -d "'" | cut -c15-)
%define WITH_LD_OPT $(echo "%{NGINX_COMPILED_FLAGS}" | grep -Eo \"\\\--with-ld-opt='[^']+'\" | tr -d "'" | cut -c15-)
%define MODULE_CONFIGURE_ARGS $(echo "--add-dynamic-module=modules/nginx-module-headers-more")

%prep
%setup -qcTn %{name}-%{_nginxver}_%{_modver}
tar --strip-components=1 -zxf %{SOURCE0}
mkdir -p modules/%{name}
cd modules/%{name}
tar --strip-components=1 -zxf %{SOURCE1}
cd ../../


%build

echo "BASE_CONFIGURE_ARGS: %{BASE_CONFIGURE_ARGS}"
echo "MODULE_CONFIGURE_ARGS: %{MODULE_CONFIGURE_ARGS}"
echo "WITH_CC_OPT: %{WITH_CC_OPT}"
echo "WITH_LD_OPT: %{WITH_LD_OPT}"

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
        --with-cc-opt="%{WITH_CC_OPT} " \
        --with-ld-opt="%{WITH_LD_OPT} " \
        --with-debug
make -f objs/Makefile %{?_smp_mflags} modules

for so in `find %{nginx_build_dir}/objs/ -type f -name "*.so"`; do
    debugso=`echo $so | sed -e "s|.so|-debug.so|"`
    mv $so $debugso
done

./configure %{BASE_CONFIGURE_ARGS} %{MODULE_CONFIGURE_ARGS} \
        --with-cc-opt="%{WITH_CC_OPT} " \
        --with-ld-opt="%{WITH_LD_OPT} "
make -f objs/Makefile %{?_smp_mflags} modules

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/doc/%{name}
%{__install} -m 644 -p %{SOURCE2} \
    $RPM_BUILD_ROOT%{_datadir}/doc/%{name}/COPYRIGHT

%{__mkdir} -p $RPM_BUILD_ROOT%{_libdir}/nginx/modules

for so in `find %{nginx_build_dir} -maxdepth 1 -type f -name "*.so"`; do
    %{__install} -m755 $so $RPM_BUILD_ROOT%{_libdir}/nginx/modules/
done





%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root)
%{_libdir}/nginx/modules/*.so


%changelog
* Wed Jul 1 2020 Dzmitry Stremkouski <mitroko@gmail.com> - 0.33-1.1
- Removing debug libs from main package

* Wed Jun 17 2020 Dzmitry Stremkouski <mitroko@gmail.com> - 0.33-1
- Compiled for nginx base version 1.18.0, module version 0.33