Name: nodejs
Version: 4.2.6
Release: 2nodesource%{?dist}
Summary: JavaScript runtime
License: MIT and ASL 2.0 and ISC and BSD
Group: Development/Languages
URL: http://nodejs.org

# Exclusive archs must match v8
ExclusiveArch: %{ix86} x86_64 %{arm}

# For NodeSource, we use the sources direct from nodejs.org/dist
Source0: node-v%{version}.tar.gz
Source1: icu4c-56_1-src.tgz

Patch1: configure-python26.patch
Patch2: install-python26.patch
Patch3: npm-python26.patch

%if 0%{?rhel} == 6
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: %{_target_cpu}
#BuildRequires: python26
#Requires: python26
BuildRequires: scl-utils
BuildRequires: devtoolset-3-gcc >= 4.8
BuildRequires: devtoolset-3-gcc-c++ >= 4.8
BuildRequires: python27
BuildRequires: python27-python
%else
BuildRequires: python
#Requires: libicu
%endif

#this corresponds to the "engine" requirement in package.json
Provides: nodejs(engine) = %{version}

# Node.js currently has a conflict with the 'node' package in Fedora
# The ham-radio group has agreed to rename their binary for us, but
# in the meantime, we're setting an explicit Conflicts: here
Conflicts: node <= 0.3.2-11

%description
Node.js is a platform built on Chrome\'s JavaScript runtime
for easily building fast, scalable network applications.
Node.js uses an event-driven, non-blocking I/O model that
makes it lightweight and efficient, perfect for data-intensive
real-time applications that run across distributed devices.

%package devel
Summary: JavaScript runtime - development headers
Group: Development/Languages
Requires: %{name}%{?_isa} == %{version}-%{release}
#Requires: nodejs-packaging

%description devel
Development headers for the Node.js JavaScript runtime.

%package docs
Summary: Node.js API documentation
Group: Documentation
BuildArch: noarch

%description docs
The API documentation for the Node.js JavaScript runtime.


%prep
%setup -q -n node-v%{version}

%if 0%{?rhel} == 5
%patch1 -p0
%patch2 -p0
%patch3 -p0
%endif

%build
export CFLAGS='%{optflags} -g -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64'
export CXXFLAGS='%{optflags} -g -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64'

%if 0%{?rhel} == 6
. /opt/rh/devtoolset-3/enable && . /opt/rh/python27/enable
./configure --prefix=%{_prefix} \
           --without-dtrace \
           --with-intl=small-icu \
           --with-icu-source=%{SOURCE1}
%else
./configure --prefix=%{_prefix} \
           --without-dtrace \
           --with-intl=small-icu \
           --with-icu-source=%{SOURCE1}
%endif

# Setting BUILDTYPE=Debug builds both release and debug binaries
make BUILDTYPE=Debug %{?_smp_mflags}

%pre
if [ -d /usr/lib/node_modules/npm ]; then
  echo "Detected old npm client, removing..."
  rm -rf /usr/lib/node_modules/npm
fi

%install
rm -rf %{buildroot}

./tools/install.py install %{buildroot} %{_prefix}

# and remove dtrace file again
rm -rf %{buildroot}/%{_prefix}/lib/dtrace

# Set the binary permissions properly
chmod 0755 %{buildroot}/%{_bindir}/node
chmod 0755 %{buildroot}/%{_bindir}/npm

# Install the debug binary and set its permissions
install -Dpm0755 out/Debug/node %{buildroot}/%{_bindir}/node_g

# own the sitelib directory
mkdir -p %{buildroot}%{_prefix}/lib/node_modules

#install documentation
mkdir -p %{buildroot}%{_defaultdocdir}/%{name}-docs-%{version}/html
cp -pr doc/* %{buildroot}%{_defaultdocdir}/%{name}-docs-%{version}/html
rm -f %{_defaultdocdir}/%{name}-docs-%{version}/html/nodejs.1
cp -p LICENSE %{buildroot}%{_defaultdocdir}/%{name}-docs-%{version}/

#node-gyp needs common.gypi too
mkdir -p %{buildroot}%{_datadir}/node
cp -p common.gypi %{buildroot}%{_datadir}/node

%files
%doc AUTHORS CHANGELOG.md COLLABORATOR_GUIDE.md CONTRIBUTING.md GOVERNANCE.md LICENSE README.md ROADMAP.md WORKING_GROUPS.md
%{_bindir}/node
%{_bindir}/npm
%{_mandir}/man1/node.*
%dir %{_prefix}/lib/node_modules
%{_prefix}/lib/node_modules/*
%dir %{_datadir}/node

%files devel
%{_bindir}/node_g
%{_includedir}/node
%{_datadir}/node/common.gypi
%{_datadir}/systemtap/tapset/node.stp
%{_docdir}/node/gdbinit

%files docs
%{_defaultdocdir}/%{name}-docs-%{version}

%changelog
* Tue Jan 26 2016 Chris Lea <chl@nodesource.com> - 4.2.6
- RHEL6 / CentOS6 support.
- Build with --with-intl=small-icu

* Thu Jan 21 2016 Chris Lea <chl@nodesource.com> - 4.2.6
- https://nodejs.org/en/blog/release/v4.2.6/

* Wed Jan 20 2016 Chris Lea <chl@nodesource.com> - 4.2.5
- https://nodejs.org/en/blog/release/v4.2.5/

* Wed Dec 23 2015 Chris Lea <chl@nodesource.com> - 4.2.4
- https://nodejs.org/en/blog/release/v4.2.4/

* Thu Dec 03 2015 Chris Lea <chl@nodesource.com> - 4.2.3
- https://nodejs.org/en/blog/release/v4.2.3/

* Thu Nov 12 2015 Chris Lea <chl@nodesource.com> - 4.2.2
- Build with --with-intl=system-icu
- Add dependency on libicu.

* Tue Nov 03 2015 Chris lea <chl@nodesource.com> - 4.2.2
- Update to 4.2.2.
- https://nodejs.org/en/blog/release/v4.2.2/

* Tue Oct 13 2015 Chris Lea <chl@nodesource.com> - 4.2.1
- Update to 4.2.1.
- https://nodejs.org/en/blog/release/v4.2.1/

* Mon Oct 12 2015 Chris Lea <chl@nodesource.com> - 4.2.0
- Update to 4.2.0.
- https://nodejs.org/en/blog/release/v4.2.0/

* Mon Oct 05 2015 Chris Lea <chl@nodesource.com> - 4.1.2
- Update to 4.1.2.
- https://nodejs.org/en/blog/release/v4.1.2/

* Wed Sep 23 2015 Chris Lea <chl@nodesource.com> - 4.1.1
- Update to 4.1.1.
- https://nodejs.org/en/blog/release/v4.1.1/

* Thu Sep 17 2015 Chris Lea <chl@nodesource.com> - 4.1.0
- Update to 4.1.0.
- https://nodejs.org/en/blog/release/v4.1.0/

* Tue Sep 08 2015 Chris Lea <chl@nodesource.com> - 4.0.0
- New major release 4.0.0.
- NodeJS and IoJS have merged.
- https://nodejs.org/en/blog/release/v4.0.0/

* Fri Jul 10 2015 Chris Lea <chl@nodesource.com> - 0.12.7-1
- Package 0.12.7 for NodeSource.
- http://blog.nodejs.org/2015/07/10/node-v0-12-7-stable/

* Fri Jul 03 2015 Chris Lea <chl@nodesource.com> - 0.12.6-1
- New upstream release.
- http://blog.nodejs.org/2015/07/03/node-v0-12-6-stable/

* Thu Jun 25 2015 Chris Lea <chl@nodesource.com> - 0.12.5-1
- New upstream release.
- http://blog.nodejs.org/2015/06/22/node-v0-12-5-stable/

* Tue Mar 31 2015 Chris Lea <chl@nodesource.com> - 0.12.2-1
- New upstream release.
- http://blog.nodejs.org/2015/03/31/node-v0-12-2-stable

* Thu Mar 26 2015 Chris Lea <chl@nodesource.com> - 0.12.1-1
- New upstream release.
- New version of Openssl to fix security issues.

* Sun Feb 22 2015 Chris Lea <chl@nodesource.com> - 0.12.0-1
- New upstream release.

* Wed Jan 28 2015 Chris Lea <chl@nodesource.com> - 0.10.36-1
- Package 0.10.36 for NodeSource.
- openssl: update to 1.0.1l
- v8: Fix debugger and strict mode regression (Julien Gilli)
- v8: don't busy loop in cpu profiler thread (Ben Noordhuis)

* Wed Dec 24 2014 Chris Lea <chl@nodesource.com> - 0.10.35-1
- Package 0.10.35 for NodeSource.
- tls: re-add 1024-bit SSL certs removed by f9456a2 (Chris Dickinson)
- timers: don't close interval timers when unrefd (Julien Gilli)
- timers: don't mutate unref list while iterating it (Julien Gilli)

* Wed Sep 17 2014 Chris Lea <chl@nodesource.com> - 0.10.32-1
- Package 0.10.32 for NodeSource.

* Mon Aug 25 2014 Chris Lea <chris.lea@gmail.com> - 0.10.31-1
- First package for NodeSource
- new upstream release
