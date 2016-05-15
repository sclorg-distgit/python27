%global scl_name_base python
%global scl_name_version 27
%global scl %{scl_name_base}%{scl_name_version}

%scl_package %scl
%global _turn_off_bytecompile 1

%global install_scl 1

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary: Package that installs %scl
Name: %scl_name
Version: 1.1
Release: 25%{?dist}
License: GPLv2+
Source0: macros.additional.%{scl}
Source1: README
Source2: LICENSE
Source3: pythondeps-scl-27.sh
BuildRequires: help2man
# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=857354
BuildRequires: iso-codes
BuildRequires: scl-utils-build
%if 0%{?install_scl}
Requires: %{scl_prefix}python
Requires: %{scl_prefix}python-jinja2
Requires: %{scl_prefix}python-nose
Requires: %{scl_prefix}python-pip
Requires: %{scl_prefix}python-simplejson
Requires: %{scl_prefix}python-setuptools
Requires: %{scl_prefix}python-sphinx
Requires: %{scl_prefix}python-sqlalchemy
Requires: %{scl_prefix}python-virtualenv
Requires: %{scl_prefix}python-wheel
Requires: %{scl_prefix}python-werkzeug
%endif

%description
This is the main package for %scl Software Collection.

%package runtime
Summary: Package that handles %scl Software Collection.
Requires: scl-utils

%description runtime
Package shipping essential scripts to work with %scl Software Collection.

%package build
Summary: Package shipping basic build configuration
Requires: scl-utils-build

%description build
Package shipping essential configuration macros to build %scl Software Collection.

%package scldevel
Summary: Package shipping development files for %scl

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.

%prep
%setup -T -c

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .

%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7
# Fix single quotes in man page. See RHBZ#1219527
#
# http://lists.gnu.org/archive/html/groff/2008-06/msg00001.html suggests that
# using "'" for quotes is correct, but the current implementation of man in 6
# mangles it when rendering.
sed -i "s/'/\\\\(aq/g" %{scl_name}.7

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_scl_scripts}/root
mkdir -p %{buildroot}%{_root_prefix}/lib/rpm/redhat
cat >> %{buildroot}%{_scl_scripts}/enable << EOF
export PATH=%{_bindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
# For systemtap
export XDG_DATA_DIRS=%{_datadir}:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}
# For pkg-config
export PKG_CONFIG_PATH=%{_libdir}/pkgconfig\${PKG_CONFIG_PATH:+:\${PKG_CONFIG_PATH}}
EOF
%scl_install

# Add the aditional macros to macros.%%{scl}-config
cat %{SOURCE0} >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config
sed -i 's|@scl@|%{scl}|g' %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config
sed -i 's|@vendorscl@|%{scl}|g' %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Create the scldevel subpackage macros
cat >> %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel << EOF
%%scl_%{scl_name_base} %{scl}
%%scl_prefix_%{scl_name_base} %{scl_prefix}
EOF

mkdir -p %{buildroot}%{_root_prefix}/lib/rpm
cp -a %{SOURCE3} %{buildroot}%{_root_prefix}/lib/rpm

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%files

%files runtime
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config
%{_root_prefix}/lib/rpm/pythondeps-scl-27.sh

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel

%changelog
* Wed Apr 20 2016 Charalampos Stratakis <cstratak@redhat.com> - 1.1-25
- Properly seperate paths for XDG_DATA_DIRS variable (rhbz#1266529)

* Fri Apr 15 2016 Charalampos Stratakis <cstratak@redhat.com> - 1.1-24
- Fix SPEC file syntax error for XDG_DATA_DIRS variable definition (rhbz#1266529)

* Wed Feb 17 2016 Robert Kuska <rkuska@redhat.com> - 1.1-23
- Insert proper value into requires/provides macros
- Use Release number 23 as there is already built version 22 in brew

* Wed Feb 17 2016 Michal Cyprian <mcyprian@redhat.com> - 1.1-19
- Add script pythondeps-scl-27.sh to manage provides and requires

* Tue Feb 16 2016 Charalampos Stratakis <cstratak@redhat.com> - 1.1-18
- Properly define XDG_DATA_DIRS variable to avoid breaking applications (rhbz#1266529)
- Escape apostrophs in metapackage manual page(rhbz#1219527)

* Tue Jan 20 2015 Slavek Kabrda <bkabrda@redhat.com> - 1.1-17
- Require python-pip and python-wheel (note: in rh-python34
  this is not necessary, because "python" depends on these).

* Mon Mar 31 2014 Honza Horak <hhorak@redhat.com> - 1.1-16
- Fix path typo in README
  Related: #1061457

* Mon Feb 17 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1-15
- Introduce README and LICENSE.
- Change version to 1.1.
Resolves: rhbz#1061457

* Wed Jan 22 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1-14
- Add scldevel subpackage.
Resolves: rhbz#1056414

* Mon Jan 20 2014 Tomas Radej <tradej@redhat.com> - 1-13
- Rebuilt with fixed scl-utils
Resolves: rhbz#1054733

* Mon Nov 25 2013 Robert Kuska <rkuska@redhat.com> - 1-12
- Add unversioned python macros for building depending packages

* Mon Sep 30 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-11
- Make building depending collections on top of python27 easier.
Resolves: rhbz#1019238

* Mon May 27 2013 Matej Stuchlik <mstuchli@redhat.com> - 1-10
- BZ966391: Another MANPATH fix.

* Thu May 23 2013 Matej Stuchlik <mstuchli@redhat.com> - 1-9
- BZ966391: MANPATH fix

* Tue May 07 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-8
- Add dependency on python-sphinx and python-nose to draw in
all the useful dependencies from the collection.

* Tue Apr 30 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-7
- Define variables in scriptlets in a really secure way (RHBZ#957208).
- Correct the sed on macros file to substitute all occurences on one line.

* Wed Apr 24 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-6
- Utilize the new package_override function to override __os_install_post.
- Move scripts to python-devel, so that it can be utilized in other
collections, that won't BR this metapackage.

* Wed Apr 24 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-5
- Delete the __os_install_post redefinition in favor of new definition
in scl-utils-build.

* Wed Apr 10 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1-4
- Define variables in enable scriptlets in a secure way (RHBZ #949000).

* Mon Dec 03 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1-3
- Rebuilt for PPC.

* Wed Oct 10 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1-2
- Enable installing the whole SCL.

* Fri Sep 14 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1-1
- Initial package.
