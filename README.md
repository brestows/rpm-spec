# rpm-spec

Spec files built on [copr.fedorainfracloud.org](https://copr.fedorainfracloud.org/).

| directory | copr project | chroots |
|---|---|---|
| `nginx/modules/` | [brestows/nginx-module](https://copr.fedorainfracloud.org/coprs/brestows/nginx-module/) | epel-8, epel-9, epel-10 |
| `lua/modules/` | [brestows/lua-modules](https://copr.fedorainfracloud.org/coprs/brestows/lua-modules/) | epel-8, epel-9 |

Each package lives in its own directory as `build.spec`, wired to copr as an SCM
package with auto-rebuild on push.

---

## nginx modules

Three dynamic modules, verified end to end on Rocky 8, 9 and 10:

| package | contents |
|---|---|
| `nginx-mod-geoip2` | `ngx_http_geoip2_module.so` |
| `nginx-module-headers-more` | `ngx_http_headers_more_filter_module.so` |
| `nginx-mod-lua` | `ngx_http_lua_module.so`, `ndk_http_module.so`, and the `resty.core` Lua library |

### Installing

```sh
# EPEL is required: nginx-mod-lua links against luajit, geoip2 against libmaxminddb.
dnf install -y epel-release

# EL8 only. The default nginx module stream is 1.14, which provides no
# nginx(abi), so dnf will refuse to install the modules against it.
dnf module enable -y nginx:1.20

dnf copr enable -y brestows/nginx-module
dnf install -y nginx nginx-mod-geoip2 nginx-module-headers-more nginx-mod-lua
```

### Enabling

**The packages install the `.so` files and stop there. Nothing is loaded
automatically.** Distributions ship a `/usr/share/nginx/modules/mod-*.conf` that
auto-enables their modules; these packages deliberately do not. A second
`load_module` for a module an admin already loads by hand aborts nginx with
`module ... is already loaded`, which is a bad way to find out during a package
upgrade.

Add the directives yourself, at the top of `/etc/nginx/nginx.conf`, in the main
context — before `events`:

```nginx
load_module "/usr/lib64/nginx/modules/ndk_http_module.so";
load_module "/usr/lib64/nginx/modules/ngx_http_lua_module.so";
load_module "/usr/lib64/nginx/modules/ngx_http_headers_more_filter_module.so";
load_module "/usr/lib64/nginx/modules/ngx_http_geoip2_module.so";
```

Two things bite here:

- **NDK must be loaded before ngx_lua.** ngx_lua depends on it.
- **The path must be absolute.** `load_module` resolves relative paths against
  nginx's `--prefix` (`/usr/share/nginx`), *not* its `--modules-path`
  (`/usr/lib64/nginx/modules`), so `load_module modules/x.so` fails with
  "cannot open shared object file".

### Known limitation: LuaJIT

`nginx-mod-lua` links against EPEL's `luajit`, which is upstream LuaJIT 2.1, not
OpenResty's `luajit2` fork. It works, but nginx logs an alert at startup and many
JIT optimizations are off. If Lua is on a hot path, package `luajit2` separately.

---

## Maintaining the nginx specs

### nginx version is pinned, on purpose

A dynamic module only loads into the exact nginx version it was compiled
against, so each spec hardcodes one version per EL release:

| | nginx | PCRE | note |
|---|---|---|---|
| EL8 | 1.20.1 | PCRE1 | module stream; default 1.14 has no `nginx(abi)` |
| EL9 | 1.20.1 | PCRE1 | plain package; streams 1.22/1.24/1.26 exist but none is default |
| EL10 | 1.26.3 | PCRE2 | no modularity; PCRE1 is gone from EL10 entirely |

`%build` compares the pinned version against the installed nginx and **aborts on
a mismatch** rather than producing a `.so` nginx will refuse to load. When a
distro bumps nginx, that check fires — which is the point. To fix it: bump
`nginx_version` *and* add the new tarball to `Source`.

### Every nginx tarball must be listed in Source

copr builds the SRPM **once**, in a builder where `%{rhel}` is undefined. mock
then unpacks that SRPM into the target chroot and re-runs `rpmbuild -bs` *there*,
where `%{rhel}` is finally 8, 9 or 10.

This splits `%if 0%{?rhel}` into two classes:

- Conditional `BuildRequires` are **safe** — the in-chroot re-parse resolves
  them, which is why `pcre-devel` vs `pcre2-devel` works.
- Conditional `Source:` lines are **not** — the SRPM only carries the sources
  selected when `%{rhel}` was undefined. The in-chroot re-parse then dies with
  `error: Bad file: SOURCES/nginx-1.26.3.tar.gz: No such file or directory`.

So both nginx tarballs are listed unconditionally and `%prep` picks one. EL8 and
EL9 hid this bug for a while: both want 1.20.1, the one tarball the SRPM carried.

### --with-compat instead of scraping `nginx -V`

These specs configure nginx with `--with-compat`, which makes the module load
into any nginx also built with it, regardless of which optional features each
enabled. RHEL's nginx is built that way.

The alternative — replaying the distro's configure flags via
`%(nginx -V 2>&1 | ...)` — is worse twice over. `%(...)` expands when the spec is
*parsed*, which for an SRPM build happens outside the buildroot, and it drags in
BuildRequires for every optional nginx feature (gd, libxslt, perl, gperftools).

Modules require `nginx(abi) = <version>`, the same virtual provide Fedora's own
`nginx-mod-*` subpackages use — not an exact nginx NEVR.

### ngx_lua and lua-resty-core move together

Since 0.10.16 ngx_lua refuses to start without the `resty.core` Lua library, and
neither it nor its `lua-resty-lrucache` dependency is packaged for EL. Both are
bundled into `nginx-mod-lua` and installed to `/usr/share/lua/5.1`, which is on
LuaJIT's compiled-in `package.path`.

`resty.core` asserts an **exact** ngx_lua version at load time. Bumping one
without the other makes nginx abort at startup with
`ngx_http_lua_module X.Y.Z required`. The current pair is ngx_lua **0.10.29** with
lua-resty-core **0.1.32**; the pair for 0.10.31 is still a release candidate.

`ngx_devel_kit` is likewise unpackaged for EL and is compiled alongside ngx_lua.

---

## Testing locally

Reproduce copr's pipeline — build the SRPM where `%{rhel}` is undefined, then let
mock rebuild it in the target chroot:

```sh
# 1. SRPM, the way copr makes it
spectool -g -R nginx-mod-lua.spec && rpmbuild -bs nginx-mod-lua.spec

# 2. rebuild in each chroot. Fedora's mock-core-configs dropped plain
#    epel-8-x86_64; use the alma+ or rocky+ variants.
mock -r alma+epel-8-x86_64  --rebuild *.src.rpm   # needs nginx:1.20:
                                                  # config_opts['module_enable'] = ['nginx:1.20']
mock -r alma+epel-9-x86_64  --rebuild *.src.rpm
mock -r alma+epel-10-x86_64 --rebuild *.src.rpm   # no module_enable: EL10 dropped modularity
```

`rpmbuild -bb` straight inside a container is *not* equivalent — it skips the
SRPM round trip and hides the `Source` bug described above.
