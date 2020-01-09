# virtual provides:
#   clufter         -> clufter-cli
Name:           clufter
Version:        0.77.1
Release:        1%{?dist}
Group:          System Environment/Base
Summary:        Tool/library for transforming/analyzing cluster configuration formats
License:        GPLv2+
URL:            https://pagure.io/%{name}

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-lxml
# following for nosetests
BuildRequires:  python-nose
# following to ensure "which bash" (and, in extension, "which sh") works
BuildRequires:  bash which
# following for UpdateTimestamps sanitization function
#BuildRequires:  diffstat

BuildRequires:  pkgconfig(libxml-2.0)

#global test_version
%global testver      %{?test_version}%{?!test_version:%{version}}

Source0:        https://people.redhat.com/jpokorny/pkgs/%{name}/%{name}-%{version}.tar.gz
Source1:        https://people.redhat.com/jpokorny/pkgs/%{name}/%{name}-%{testver}-tests.tar.xz
Patch0:         https://pagure.io/clufter/c/ed6c3c850938622a185effd332ce6b553734cad4.patch

%description
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

%package cli
Group:          System Environment/Base
Summary:        Tool for transforming/analyzing cluster configuration formats
Provides:       %{name} = %{version}-%{release}

# cannot get bash-completion from EPEL6 into the buildroot
#BuildRequires:  bash-completion

BuildRequires:  help2man

# following for pkg_resources module
Requires:       python-setuptools
Requires:       python-%{name} = %{version}-%{release}
Requires:       %{_bindir}/nano
BuildArch:      noarch

%description cli
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

This package contains %{name} command-line interface for the underlying
library (packaged as python-%{name}).

%package -n python-%{name}
Group:          System Environment/Libraries
Summary:        Library for transforming/analyzing cluster configuration formats
License:        GPLv2+ and GFDL

Requires:       %{name}-bin = %{version}-%{release}
Requires:       python-lxml
BuildArch:      noarch

%description -n python-%{name}
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

This package contains %{name} library including built-in plugins.

%package bin
Group:          System Environment/Libraries
Summary:        Common internal compiled files for %{name}
License:        GPLv2+

Requires:       %{name}-common = %{version}-%{release}

%description bin
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

This package contains internal, arch-specific files for %{name}.

%package common
Group:          System Environment/Libraries
Summary:        Common internal data files for %{name}
License:        GPLv2+
BuildArch:      noarch

%description common
While primarily aimed at (CMAN,rgmanager)->(Corosync/CMAN,Pacemaker) cluster
stacks configuration conversion (as per RHEL trend), the command-filter-format
framework (capable of XSLT) offers also other uses through its plugin library.

This package contains internal, arch-agnostic files for %{name}.

%package lib-general
Group:          System Environment/Libraries
Summary:        Extra %{name} plugins usable for/as generic/auxiliary products
Requires:       python-%{name} = %{version}-%{release}
BuildArch:      noarch

%description lib-general
This package contains set of additional plugins targeting variety of generic
formats often serving as a byproducts in the intermediate steps of the overall
process arrangement: either experimental commands or internally unused,
reusable formats and filters.

%package lib-ccs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing CMAN configuration
Requires:       %{name}-lib-general = %{version}-%{release}
BuildArch:      noarch

%description lib-ccs
This package contains set of additional plugins targeting CMAN cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.

%package lib-pcs
Group:          System Environment/Libraries
Summary:        Extra plugins for transforming/analyzing Pacemaker configuration
Requires:       %{name}-lib-general = %{version}-%{release}
BuildArch:      noarch

%description lib-pcs
This package contains set of additional plugins targeting Pacemaker cluster
configuration: either experimental commands or internally unused, reusable
formats and filters.

%prep
%setup -b 1

%if "%{testver}" != "%{version}"
    %{__cp} -a ../"%{name}-%{testver}"/* .
%endif
%patch0 -p1

## for some esoteric reason, the line above has to be empty
%{__python} setup.py saveopts -f setup.cfg pkg_prepare \
                     --ccs-flatten='%{_libexecdir}/%{name}-%{version}/ccs_flatten' \
                     --editor='%{_bindir}/nano' \
                     --extplugins-shared='%{_datarootdir}/%{name}/ext-plugins' \
                     --ra-metadata-dir='%{_datadir}/cluster' \
                     --ra-metadata-ext='metadata' \
                     --shell-posix='%(which sh 2>/dev/null || echo /bin/SHELL-POSIX)' \
                     --shell-bashlike='%(which bash 2>/dev/null || echo /bin/SHELL-BASHLIKE)'
%{__python} setup.py saveopts -f setup.cfg pkg_prepare \
--report-bugs='https://bugzilla.redhat.com/enter_bug.cgi?product=Red%20Hat%20Enterprise%20Linux%206&component=clufter'
# make Python interpreter executation sane (via -Es flags)
%{__python} setup.py saveopts -f setup.cfg build_scripts \
                     --executable='%{__python} -Es'
%build
%{__python} setup.py build
%{__python} ./run-dev --skip-ext --completion-bash 2>/dev/null \
  | sed 's|run[-_]dev|%{name}|g' > .bashcomp
# generate man pages (proper commands and aliases from a sorted sequence)
%{__mkdir_p} -- .manpages/man1
{ echo; ./run-dev -l | sed -n 's|^  \(\S\+\).*|\1|p' | sort; } > .subcmds
sed -e 's:\(.\+\):\\\&\\fIrun_dev-\1\\fR\\\|(1), :' \
  -e '1s|\(.*\)|\[SEE ALSO\]\n|' \
  -e '$s|\(.*\)|\1\nand perhaps more|' \
  .subcmds > .see-also
help2man -N -h -H -i .see-also \
  -n "$(sed -n '2s|[^(]\+(\([^)]\+\))|\1|p' README)" ./run-dev \
  | sed 's|run\\\?[-_]dev|%{name}|g' \
  > ".manpages/man1/%{name}.1"
while read cmd; do
  [ -n "${cmd}" ] || continue
  echo -e "#\!/bin/sh\n{ [ \$# -ge 1 ] && [ \"\$1\" = \"--version\" ] \
  && ./run-dev \"\$@\" || ./run-dev \"${cmd}\" \"\$@\"; }" > ".tmp-${cmd}"
  chmod +x ".tmp-${cmd}"
  grep -v "^${cmd}\$" .subcmds \
    | grep -e '^$' -e "$(echo ${cmd} | cut -d- -f1)\(-\|\$\)" \
    | sed -e 's:\(.\+\):\\\&\\fIrun_dev-\1\\fR\\\|(1), :' \
      -e '1s|\(.*\)|\[SEE ALSO\]\n\\\&\\fIrun_dev\\fR\\\|(1), \n|' \
      -e '$s|\(.*\)|\1\nand perhaps more|' > .see-also
  # XXX uses ";;&" bashism
  case "${cmd}" in
  ccs[2-]*)
    sed -i \
      '1s:\(.*\):\1\n\\\&\\fIcluster.conf\\fR\\\|(5), \\\&\\fIccs\\fR\\\|(7), :' \
    .see-also
    ;;&
  ccs2pcs*)
    sed -i \
      '1s:\(.*\):\1\n\\\&\\fI%{_defaultdocdir}/%{name}-%{version}/rgmanager-pacemaker\\fR\\\|, :' \
    .see-also
    ;;&
  *[2-]pcscmd*)
    sed -i '1s:\(.*\):\1\n\\\&\\fIpcs\\fR\\\|(8), :' .see-also
    ;;&
  esac
  help2man -N -h -H -i .see-also -n "${cmd}" "./.tmp-${cmd}" \
    | sed 's|run\\\?[-_]dev|%{name}|g' \
  > ".manpages/man1/%{name}-${cmd}.1"
done < .subcmds

%install

# '--root' implies setuptools involves distutils to do old-style install
%{__python} setup.py install --skip-build --root '%{buildroot}'
# following is needed due to umask 022 not taking effect(?) leading to 775
%{__chmod} -- g-w '%{buildroot}%{_libexecdir}/%{name}-%{version}/ccs_flatten'
# fix excessive script interpreting "executable" quoting with old setuptools:
# https://github.com/pypa/setuptools/issues/188
# https://bugzilla.redhat.com/1353934
sed -i '1s|^\(#!\)"\(.*\)"$|\1\2|' '%{buildroot}%{_bindir}/%{name}'
# %%{_bindir}/%%{name} should have been created
test -f '%{buildroot}%{_bindir}/%{name}' \
  || %{__install} -D -pm 644 -- '%{buildroot}%{_bindir}/%{name}' \
                                '%{buildroot}%{_bindir}/%{name}'

# move ext-plugins from python-specific locations to a single common one
# incl. the different sorts of precompiled bytecodes
%{__mkdir_p} -- '%{buildroot}%{_datarootdir}/%{name}/ext-plugins'
mv -t '%{buildroot}%{_datarootdir}/%{name}/ext-plugins' \
   -- '%{buildroot}%{python_sitelib}/%{name}'/ext-plugins/*/

declare bashcompdir="$(pkg-config --variable=completionsdir bash-completion \
                       || echo '%{_sysconfdir}/bash_completion.d')"
declare bashcomp="${bashcompdir}/%{name}"
%{__install} -D -pm 644 -- \
  .bashcomp '%{buildroot}%{_sysconfdir}/%{name}/bash-completion'
%{__mkdir_p} -- "%{buildroot}${bashcompdir}"
ln -s '%{_sysconfdir}/%{name}/bash-completion' "%{buildroot}${bashcomp}"
# own %%{_datadir}/bash-completion in case of ...bash-completion/completions,
# more generally any path up to any of /, /usr, /usr/share, /etc
while true; do
  test "$(dirname "${bashcompdir}")" != "/" \
  && test "$(dirname "${bashcompdir}")" != "%{_prefix}" \
  && test "$(dirname "${bashcompdir}")" != "%{_datadir}" \
  && test "$(dirname "${bashcompdir}")" != "%{_sysconfdir}" \
  || break
  bashcompdir="$(dirname "${bashcompdir}")"
done
cat >.bashcomp-files <<-EOF
	${bashcompdir}
	%dir %{_sysconfdir}/%{name}
	%verify(not size md5 mtime) %{_sysconfdir}/%{name}/bash-completion
EOF
%{__mkdir_p} -- '%{buildroot}%{_mandir}'
%{__cp} -a -t '%{buildroot}%{_mandir}' -- .manpages/*
%{__mkdir_p} -- '%{buildroot}%{_defaultdocdir}/%{name}-%{version}'
%{__cp} -a -t '%{buildroot}%{_defaultdocdir}/%{name}-%{version}' \
           -- gpl-2.0.txt doc/*.txt doc/rgmanager-pacemaker

%check
# just a basic sanity check
# we need to massage RA metadata files and PATH so the local run works
# XXX we could also inject buildroot's site_packages dir to PYTHONPATH
declare ret=0 \
        ccs_flatten_dir="$(dirname '%{buildroot}%{_libexecdir}/%{name}-%{version}/ccs_flatten')"
ln -s '%{buildroot}%{_datadir}/cluster'/*.'metadata' \
      "${ccs_flatten_dir}"
PATH="${PATH:+${PATH}:}${ccs_flatten_dir}" PYTHONEXEC="%{__python} -Es" ./run-tests
ret=$?
%{__rm} -f -- "${ccs_flatten_dir}"/*.'metadata'
[ ${ret} -eq 0 ] || exit ${ret}

%post cli
if [ $1 -gt 1 ]; then  # no gain regenerating it w/ fresh install (same result)
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
%{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :
fi

%post lib-general
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
# if the completion file is not present, suppose it is not desired
test -x '%{_bindir}/%{name}' && test -f "${bashcomp}" \
  && %{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :

%post lib-ccs
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
# if the completion file is not present, suppose it is not desired
test -x '%{_bindir}/%{name}' && test -f "${bashcomp}" \
  && %{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :

%post lib-pcs
declare bashcomp="%{_sysconfdir}/%{name}/bash-completion"
# if the completion file is not present, suppose it is not desired
test -x '%{_bindir}/%{name}' && test -f "${bashcomp}" \
  && %{_bindir}/%{name} --completion-bash > "${bashcomp}" 2>/dev/null || :

%files cli -f .bashcomp-files
%{_mandir}/man1/*.1*
%{_bindir}/%{name}

%files -n python-%{name}
%{python_sitelib}/%{name}
%{python_sitelib}/%{name}-*.egg-info

%files bin
%{_libexecdir}/%{name}-%{version}

%files common
%{_datadir}/cluster
%{_datarootdir}/%{name}
%dir %{_defaultdocdir}/%{name}-%{version}
%{_defaultdocdir}/%{name}-%{version}/*[^[:digit:]]
%doc %{_defaultdocdir}/%{name}-%{version}/*[[:digit:]].txt

%files lib-general
%{_datarootdir}/%{name}/ext-plugins/lib-general

%files lib-ccs
%{_datarootdir}/%{name}/ext-plugins/lib-ccs

%files lib-pcs
%{_datarootdir}/%{name}/ext-plugins/lib-pcs

%changelog
* Thu Mar 15 2018 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.77.1-1
- split -bin and -common packages, the former becoming the only arch-specific
- also move python-specific (entry points, main files) back from -cli package
- move nano fallback editor dependency to -cli package [PGissue#1]
- bump upstream package, see https://pagure.io/clufter/releases

* Wed Jan 18 2017 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.59.8-1
- bump upstream package, see
  https://github.com/jnpkrn/clufter/releases/tag/v0.59.8

* Mon Dec 12 2016 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.59.7-1
- bump upstream package, see
  https://github.com/jnpkrn/clufter/releases/tag/v0.59.7

* Thu Oct 20 2016 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.59.6-1
- bump upstream package, see https://pagure.io/clufter/releases
  (v0.56.3, v0.57.0, v0.58.0, v0.59.0 ... v0.59.6)
- make Python interpreter execution sane

* Fri Mar 18 2016 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.56.2-1
- move entry_points.txt to clufter-cli sub-package
- bump upstream package, see
  https://github.com/jnpkrn/clufter/releases/tag/v0.56.2

* Tue Feb 09 2016 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.56.1-1
- bump upstream package, see
  https://github.com/jnpkrn/clufter/releases/tag/v0.56.1

* Mon Feb 01 2016 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.56.0-1
- general spec file refresh (pagure.io as a default project base, etc.)
- bump upstream package, see
  https://github.com/jnpkrn/clufter/releases/tag/v0.56.0

* Tue Dec 22 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.55.0-3
- auto-generate SEE ALSO sections for the man pages
- utilize test suite in the check phase of the build process
- bump upstream package (intentional jump on upstream front),
  see https://github.com/jnpkrn/clufter/releases/tag/v0.55.0

* Thu Oct 08 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.50.5-1
- generate man pages also for built-in commands
- bump upstream package

* Fri May 29 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.11.2-1
- move completion module to clufter-cli sub-package
- bump upstream package

* Mon May 18 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.11.1-1
- bump upstream package

* Wed Apr 15 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.11.0-1
- bump upstream package

* Fri Mar 20 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.3-1
- bump upstream package

* Mon Mar 16 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.2-1
- bump upstream package

* Fri Mar 06 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.1-2
- packaging fixes (%{name}-cli requires python-setuptools, adjust for
  older schema of Bash completions)

* Fri Mar 06 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.1-1
- bump upstream package

* Thu Feb 26 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.10.0-1
- packaging enhacements (structure, redundancy, ownership, scriptlets, symlink)
- version bump so as not to collide with python-clufter co-packaged with pcs

* Tue Jan 20 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.3.5-1
- packaging enhancements (pkg-config, license tag)

* Wed Jan 14 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.3.4-1
- packaging enhancements (permissions, ownership)
- man page for CLI frontend now included

* Tue Jan 13 2015 Jan Pokorný <jpokorny+rpm-clufter@redhat.com> - 0.3.3-1
- initial build
