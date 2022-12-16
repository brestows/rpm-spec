Summary: GeoIP2 module for nginx
Name: nginx-mod-geoip2
Version: 3.4
Release: 2%{?dist}
Vendor: brestows
URL: https://github.com/leev/ngx_http_geoip2_module

%define _modname            geoip2
%define _nginxver           1.20.1
%define nginx_config_dir    %{_sysconfdir}/nginx
%define nginx_build_dir     %{_builddir}/nginx-%{_nginxver}

Source0: https://nginx.org/download/nginx-%{_nginxver}.tar.gz
Source1: https://github.com/leev/ngx_http_geoip2_module/archive/%{version}/%{_modname}-%{version}.tar.gz

Requires: nginx = 1:%{_nginxver}
Requires: libmaxminddb
BuildRequires: nginx
BuildRequires: libtool
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: openssl-devel
BuildRequires: pcre-devel
BuildRequires: zlib-devel
BuildRequires: perl-devel
BuildRequires: gd-devel
BuildRequires: libmaxminddb-devel
BuildRequires: libxslt-devel
BuildRequires: perl-devel
BuildRequires: perl(ExtUtils::Embed)
BuildRequires: gperftools-devel

License: BSD

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
GeoIP2 module for nginx.

%prep
%setup -q -n nginx-%{_nginxver}
%setup -T -D -b 1 -n ngx_http_%{_modname}_module-%{version}

%build
cd %{_builddir}/nginx-%{_nginxver}
./configure %(nginx -V 2>&1 | grep 'configure arguments' | sed -r 's@^[^:]+: @@') --add-dynamic-module=../ngx_http_%{_modname}_module-%{version}
make modules

%install
%{__rm} -rf %{buildroot}

%{__install} -Dm755 %{nginx_build_dir}/objs/ngx_http_%{_modname}_module.so \
    $RPM_BUILD_ROOT%{_libdir}/nginx/modules/ngx_http_%{_modname}_module.so

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_libdir}/nginx/modules/*.so
